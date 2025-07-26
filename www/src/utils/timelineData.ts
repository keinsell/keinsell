import { Octokit } from "@octokit/rest";
import { getCollection } from "astro:content";
import type { TimelineItem } from "../components/Timeline.astro";

export interface GitHubConfig {
  username: string;
  token?: string;
}

export class GitHubTimelineService {
  private octokit: Octokit;
  private username: string;

  constructor(config: GitHubConfig) {
    this.username = config.username;
    this.octokit = new Octokit({
      auth: config.token,
    });
  }

  async getRecentActivity(
    limit: number = 50,
    days: number = 30,
  ): Promise<TimelineItem[]> {
    try {
      const events = await this.octokit.rest.activity.listPublicEventsForUser({
        username: this.username,
        per_page: 100, // Get more to filter down
      });

      const items: TimelineItem[] = [];
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - days);

      for (const event of events.data) {
        if (items.length >= limit) break;

        const eventDate = new Date(event.created_at);
        if (eventDate < cutoffDate) continue;

        let item: TimelineItem | null = null;

        switch (event.type) {
          case "PushEvent":
            item = this.createPushEventItem(event);
            break;
          case "CreateEvent":
            if (event.payload.ref_type === "repository") {
              item = this.createRepoCreatedItem(event);
            }
            break;
          case "IssuesEvent":
            if (event.payload.action === "opened") {
              item = this.createIssueItem(event);
            }
            break;
          case "PullRequestEvent":
            if (event.payload.action === "opened") {
              item = this.createPullRequestItem(event);
            }
            break;
        }

        if (item) {
          items.push(item);
        }
      }

      return items;
    } catch (error) {
      console.error("Error fetching GitHub activity:", error);
      return [];
    }
  }

  private createPushEventItem(event: any): TimelineItem | null {
    const commits = event.payload.commits || [];
    if (commits.length === 0) return null;

    const commit = commits[0]; // Get the latest commit
    const repoName = event.repo.name;
    const commitLines = commit.message.split("\n");
    const commitTitle = commitLines[0]; // First line
    const commitDescription = commitLines.slice(1).join("\n").trim(); // Rest as description

    return {
      id: `github-push-${event.id}`,
      type: "commit",
      title: this.truncateText(commitTitle, 80),
      description: commitDescription || undefined,
      date: new Date(event.created_at),
      url: `https://github.com/${repoName}/commit/${commit.sha}`,
      repo: repoName.split("/")[1], // Just the repo name, not owner/repo
    };
  }

  private createRepoCreatedItem(event: any): TimelineItem {
    return {
      id: `github-create-${event.id}`,
      type: "repo",
      title: `Created repository ${event.repo.name.split("/")[1]}`,
      description: undefined,
      date: new Date(event.created_at),
      url: `https://github.com/${event.repo.name}`,
      repo: event.repo.name.split("/")[1],
    };
  }

  private createIssueItem(event: any): TimelineItem {
    return {
      id: `github-issue-${event.id}`,
      type: "issue",
      title: `Opened issue: ${this.truncateText(event.payload.issue.title, 60)}`,
      description: undefined,
      date: new Date(event.created_at),
      url: event.payload.issue.html_url,
      repo: event.repo.name.split("/")[1],
    };
  }

  private createPullRequestItem(event: any): TimelineItem {
    return {
      id: `github-pr-${event.id}`,
      type: "pr",
      title: `Opened PR: ${this.truncateText(event.payload.pull_request.title, 60)}`,
      description: undefined,
      date: new Date(event.created_at),
      url: event.payload.pull_request.html_url,
      repo: event.repo.name.split("/")[1],
    };
  }

  private truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + "...";
  }
}

// Configuration helper
export function getGitHubConfig(): GitHubConfig {
  // Check for environment variables
  if (typeof process !== "undefined" && process.env) {
    return {
      username: process.env.GITHUB_USERNAME || "keinsell",
      token: process.env.GITHUB_TOKEN,
    };
  }

  // Fallback for client-side
  return {
    username: "keinsell",
  };
}

// Blog posts service
export async function getBlogPosts(days: number = 30): Promise<TimelineItem[]> {
  try {
    const blogEntries = await getCollection("blog");
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return blogEntries
      .filter((post) => post.data.pubDate >= cutoffDate)
      .map((post) => ({
        id: `blog-${post.id}`,
        type: "post" as const,
        title: post.data.title,
        description: post.data.description,
        date: post.data.pubDate,
        url: `/blog/${post.id}`,
        repo: undefined,
      }))
      .sort((a, b) => b.date.getTime() - a.date.getTime());
  } catch (error) {
    console.error("Failed to fetch blog posts:", error);
    return [];
  }
}

// Paginated timeline data interface
export interface PaginatedTimelineData {
  items: TimelineItem[];
  currentPage: number;
  hasMore: boolean;
  totalItems: number;
}

// Main function to get paginated timeline data
export async function getTimelineData(
  page: number = 1,
  itemsPerPage: number = 20,
): Promise<PaginatedTimelineData> {
  const config = getGitHubConfig();
  const service = new GitHubTimelineService(config);

  try {
    const [githubActivity, blogPosts] = await Promise.all([
      service.getRecentActivity(100, 90), // Get more items for pagination
      getBlogPosts(90), // Blog posts from last 90 days
    ]);

    // Combine and sort all items by date
    const allItems = [...githubActivity, ...blogPosts];
    allItems.sort((a, b) => b.date.getTime() - a.date.getTime());

    // Calculate pagination
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedItems = allItems.slice(startIndex, endIndex);

    return {
      items: paginatedItems,
      currentPage: page,
      hasMore: endIndex < allItems.length,
      totalItems: allItems.length,
    };
  } catch (error) {
    console.error("Failed to fetch timeline data:", error);
    const mockItems = generateMockData();
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;

    return {
      items: mockItems.slice(startIndex, endIndex),
      currentPage: page,
      hasMore: endIndex < mockItems.length,
      totalItems: mockItems.length,
    };
  }
}

// Simple mock data for development/fallback
export function generateMockData(): TimelineItem[] {
  const now = Date.now();

  return [
    {
      id: "mock-1",
      type: "commit",
      title: "Add TypeScript support for API endpoints",
      description:
        "Refactored authentication middleware and added proper type definitions for better developer experience.",
      date: new Date(now - 2 * 60 * 60 * 1000),
      url: "https://github.com/keinsell/example/commit/abc123",
      repo: "api-server",
    },
    {
      id: "mock-2",
      type: "commit",
      title: "Fix memory leak in background workers",
      description:
        "Identified and resolved a critical memory leak that was affecting long-running background processes.",
      date: new Date(now - 6 * 60 * 60 * 1000),
      url: "https://github.com/keinsell/example/commit/def456",
      repo: "worker-service",
    },
    {
      id: "mock-3",
      type: "post",
      title: "New Firmware Has Arrived",
      description:
        "Personal reflections of experience with the software industry, career decisions, and future aspirations.",
      date: new Date(now - 1 * 24 * 60 * 60 * 1000),
      url: "/blog/new-firmware-has-arrived",
    },
    {
      id: "mock-4",
      type: "commit",
      title: "Implement dark mode support",
      description:
        "Added system preference detection and manual toggle for dark/light themes across the application.",
      date: new Date(now - 2 * 24 * 60 * 60 * 1000),
      url: "https://github.com/keinsell/example/commit/ghi789",
      repo: "frontend-app",
    },
    {
      id: "mock-5",
      type: "commit",
      title: "Update CI/CD pipeline configuration",
      description:
        "Optimized build process and added automated testing stages. Build time reduced by 40%.",
      date: new Date(now - 3 * 24 * 60 * 60 * 1000),
      url: "https://github.com/keinsell/example/commit/jkl012",
      repo: "devops-config",
    },
  ];
}
