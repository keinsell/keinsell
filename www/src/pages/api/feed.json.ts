import type { APIRoute } from "astro";
import { getTimelineData } from "../../utils/timelineData";

export const GET: APIRoute = async ({ url }) => {
  try {
    const page = parseInt(url.searchParams.get("page") || "1", 10);
    const limit = parseInt(url.searchParams.get("limit") || "15", 10);

    // Validate parameters
    if (page < 1 || limit < 1 || limit > 50) {
      return new Response(
        JSON.stringify({ error: "Invalid page or limit parameter" }),
        {
          status: 400,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
    }

    const timelineData = await getTimelineData(page, limit);

    return new Response(JSON.stringify(timelineData), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=300", // Cache for 5 minutes
      },
    });
  } catch (error) {
    console.error("API Error:", error);

    return new Response(
      JSON.stringify({
        error: "Failed to fetch timeline data",
        message: error instanceof Error ? error.message : "Unknown error"
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
  }
};
