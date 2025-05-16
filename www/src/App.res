@react.component
let make = () => {
  <div className="min-h-screen bg-gray-50 text-gray-800 p-6 max-w-4xl mx-auto">
    <header className="mb-12">
      <pre className="text-xs sm:text-sm font-mono mb-4 text-gray-600 overflow-x-auto">
        {React.string(`
                  ,,__
        ..  ..   / o._)                   .---.
       /--'/--\\  \\-'||        .----.    .'     '.
      /        \\_/ / |      .'      '..'         '-.
    .'\\  \\__\\  __.'.'     .'          i-._
        )\\ |  )\\ |      _.'
    // \\\\ // \\\\
    ||_  \\\\|_  \\\\_
    '--' '--'' '--'
`)}
      </pre>
      <h1 className="text-4xl font-bold mb-2"> {React.string("Architect on the desert")} </h1>
      <p className="text-xl">
        {React.string("I'm Jakub Olan (aka. \"keinsell\")")}
      </p>
    </header>

    <main className="space-y-10">
      <section>
        <p className="mb-4">
          {React.string("Previously holding position of Lead Software Engineer at stepapp.pl up to November 2024, I don't feel like a coming back yet but let's say I'm trying to find somewhat company, team or a partner that would have idea what to do with their time and resources.")}
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4"> {React.string("Recent news")} </h2>
        <p className="mb-2">
          {React.string("During my break I have overcome fundamentals of Rust and built understanding of memory management model with borrowing and ownership, loved a lot of approaches starting from compiler errors, effortless tooling, community driven development and so on.")}
        </p>
        <p>
          {React.string("I find out that Rust isn't the best language for application development which was my primary scope of work to this time, as when we will look at OCaml we also have a lot of common with Rust except it's garbage collected and is allowing for rapid prototyping while maintaining correctness by Handley-Miller type system.")}
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4"> {React.string("What I'm looking for?")} </h2>
        <p className="mb-2">
          {React.string("I am looking for a postion where I would be able to contribute freely and autonomously, somewhere where speed isn't the only metric of code quality, but also measuring the amount of bugs that are being introduced and amount of time that are being spent on fixing them. Let's be honest, I want to see coffee at morning not pager that company is burining down.")}
        </p>
        <p className="mb-2">
          {React.string("Considering today's state of knowledge and it's accessibility, I would rather bet on Rust/OCaml internship than Senior+ position in TypeScript, as my recent experiences with Rust ecosystem clearly shown that TypeScript even through wider adoption is still lacking right tooling, serious ecosystem and eventually type-system that would be not another foundation for trust issues.")}
        </p>
        <p>
          {React.string("Environment where I can be myself and there is limited amount of bullshit around as with this particular shot I probably paying with burnout so I want it be explicitly stated, as far as my insanity goes I am not going to handle things at that cost, therefore my financial needs are not that high.")}
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4"> {React.string("What I have to offer?")} </h2>
        <p className="mb-2">
          {React.string("Not much, at least not today, not in time where I don't feel like waking up from my bed.")}
        </p>
        <p>
          {React.string("If I will figure out this part, then it's software as a whole to majority of plaforms, be it web, desktop, mobile or purely server-side/local software, I can take part in creative process, engineering, management and even eventually at business operations except I do not have a clue about how to handle people, nor experience that you would trust. It's not a problem to me to learn anything that I do not know as not as time constraints are not that high - chance where I could do 14h/d are over now - not like I am a prove of my word, but! As far as I been in different products and companies there were no single company where I could not contribute in a first 3 days, so eventually you can lay off on a 3-5th day and nobody will cry about it.")}
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4"> {React.string("Professional experience")} </h2>
        
        <div className="mb-6">
          <h3 className="text-xl font-medium mb-2"> {React.string("2023-2024 | Lead Back-End Developer @ stepapp.pl")} </h3>
          <p className="mb-2">
            {React.string("Led the software development ( 65% ownership) of a subscription-based home cleaning service platform. Brownfield project.")}
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              {React.string("Developed and maintained brownfield backend-for-frontend (BFF) within a SOA architecture using Domain-Driven Design (DDD) and Data-Driven Design (that other DDD) principles.")}
            </li>
            <li>
              {React.string("Participated in Event Storming, and Context Mapping to define and manage bounded contexts, minimize coupling and resolve dependency problems from previous iterations.")}
            </li>
            <li>
              {React.string("Implemented public GraphQL API (storefront) following industry standards (RFCs 3339, 9457, 6638) and integrating crucial middleware components for Authentication (AuthN), Authorization (AuthZ), Caching (Keyv/Local/Redis) and data loading (Dataloader with Prisma, TypeORM, and PostgreSQL)")}
            </li>
            <li>
              {React.string("Spearheaded the full software development lifecycle (research, design, implementation, testing, deployment, and maintenance) for multi-provider Payment Gateway (Stripe, Stripe Billing, manual transactions), a bespoke Content Management System (CMS), a dynamic Checkout/Storefront, and unfinished CalDAV-based appointment system.")}
            </li>
            <li>
              {React.string("Collaborated with DevOps to manage cloud infrastructure on AWS using Infrastructure-as-Code (IaC) (Terraform/Terragrunt).")}
            </li>
            <li>
              {React.string("Integrated key AWS services, including AppRunner, RDS (PostgreSQL), ElastiCache (Redis), and Secrets Manager, along with JavaScript ecosystem (TypeORM, Prisma)")}
            </li>
            <li>
              {React.string("Developed and maintained an automated release pipeline (ARA) using GitHub Actions, git-cliff and Docker Bake.")}
            </li>
            <li>
              {React.string("Enhanced developer experience by creating reproducible development environments using Nix (Flakes and devenv), supporting both devcontainers and bare-metal installations.")}
            </li>
            <li>
              {React.string("Implemented comprehensive application observability using OpenTelemetry and NewRelic, integrated with request tracing context and AsyncLocalStorage.")}
            </li>
            <li>
              {React.string("Employed \"agile\" kanban methodologies, upstream monitoring, and documentation efforts (system and domain) using Git Flow and trunk-based development practices.")}
            </li>
          </ul>
        </div>
        
        <div className="mb-6">
          <h3 className="text-xl font-medium mb-2"> {React.string("2022 | Back-End Developer @ nextrope.com")} </h3>
          <p className="mb-2">
            {React.string("Developed and maintained RESTful APIs for blockchain-based products using TypeScript.")}
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              {React.string("Development and testing of RESTful APIs developed with usage of TypeScript (or rather JavaScript in TypeScript) programming language on Loopback 4 and Nest.js frameworks.")}
            </li>
            <li>
              {React.string("Implementation of persistance mechanisms based on traditional RDBMS (PostgreSQL) and decentralized object storage (IFPS) to build \"decentralized\" solutions.")}
            </li>
            <li>
              {React.string("Maintainment, development and quality assurance of legacy codebase related to investment portal for initial coin offerings, yet without access to any critical infrastructure.")}
            </li>
            <li>
              {React.string("Integration with ERC-20 and ERC (NFT) smart contracts on Ethereum and Polygon networks.")}
            </li>
            <li>
              {React.string("Research, Design and Development of blockchain-based products (dApps) with usage of Event-Driven Architecture (EDA) based on Capture Data Change (CDC) technology.")}
            </li>
            <li>
              {React.string("Participation in process of maintainable and development of platform to distribute Ethereum ERC-20 Standard Tokens for FIAT currencies (Initial Coin Offering process)")}
            </li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-xl font-medium mb-2"> {React.string("2019-2020 | Freelance Full-Stack Developer")} </h3>
          <ul className="list-disc pl-6">
            <li>
              {React.string("Design, Development, Deployment and Maintenance of web applications created with usage of JavaScript, TypeScript, React, Node.js, Express, PostgreSQL/MongoDB, HTML, CSS, and other related technologies.")}
            </li>
          </ul>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4"> {React.string("Personal projects")} </h2>
        <div>
          <h3 className="text-xl font-medium mb-2"> {React.string("Dec 2024 - Present | neuronek")} </h3>
          <p className="mb-2">
            {React.string("Rust-based terminal application which was made to track my intake of caffeine and protect me against potentially unwanted sleep schedule interruptions, utilizing my neuroscience and pharmakinetic knowledge I have decided to also calculate most efficient times to write second coffee to maintain a steady and predictable peak.")}
          </p>
          <a href="https://github.com/keinsell/neuronek-cli" className="text-blue-600 hover:underline">
            {React.string("https://github.com/keinsell/neuronek-cli")}
          </a>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4"> {React.string("How to contact me?")} </h2>
        <p>
          {React.string("Every possible method of contact is available on my website ")}
          <a href="https://keinsell.link" className="text-blue-600 hover:underline">
            {React.string("keinsell.link")}
          </a>
        </p>
      </section>
    </main>

    <footer className="mt-12 pt-6 border-t border-gray-200 text-gray-500 text-sm">
      <p>
        {React.string("© 2024 Jakub Olan")}
      </p>
    </footer>
  </div>
}