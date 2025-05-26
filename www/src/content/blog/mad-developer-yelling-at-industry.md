---
title: 'I been there just a fucking year, WTF?!'
description: 'software industry’s quality has eroded under endless cycles of plug-and-play frameworks, microservices hype, and vendor lock-in, and it calls for a return to disciplined, minimal-trust engineering—deleting untested code, enforcing strict linting and environment consistency, and always planning for failure—to build robust, maintainable systems you can confidently hand off.'
pubDate: 'Jul 08 2022'
heroImage: '/blog-placeholder-3.jpg'
tags: ['rant']
collection: 'tools-and-productivity'
order: 1
---

Maybe I'm the only one, or perhaps not, but from my perspective, the software industry has been experiencing its
greatest decline in quality for several years now. GitHub has become flooded with subpar frameworks, each trying to
rectify the shortcomings of its predecessors in endless cycles. This is largely due to some developers who lack the
skill to write their own abstractions and rely instead on solutions that save them from writing a few lines of code.
Nobody seems willing to invest effort into software; everyone looks for the simplest solution, which inevitably leads to
complications over time. In recent years, I've seen a significant decline in software developers' abilities. I remember
developers who could handle everything on their own, regardless of the tools they had - setting up Unix servers, moving
binaries, adding them to systemctl. Nowadays, it seems every developer needs 50 different tools just to build something,
often relying on 80 different APIs integrated into their software system. Every time I see people using AWS with their
fancy CDKs and AWS SDKs integrated into software (95% of the time, integrated to the extent that migrating away from AWS
would mean the suicide of the entire company due to the costs of rewriting), I wonder what went wrong with this
industry. What if AWS doubles its prices? You wouldn't even be able to migrate; AWS owns your application, and there
would be nothing you could do about it. While AWS is used here as an example, people tend to do this with any other
library, SaaS, PaaS, etc.

Maybe it's just me, a person who sees problems in all of this as my ego is a control-freak wanting to have control over things, especially since I'm the one maintaining the software. As an engineer, I'm the one who faces the consequences of poor decisions in software, along with the business if such software is a core product. I've faced a lot of criticism for my way of building software, mostly from novice developers who have done a bootcamp and do not understand the code, libraries, or services they use. Some of these developers resort to design patterns merely to seem knowledgeable, only to later implement the most counterintuitive antipatterns due to a lack of understanding. They often propose solutions before fully understanding the problem and the process. The reality is, they don't have the solution.

I've observed people debating about microservices, serverless technology, what's beneficial, and what's scalable - but do they truly understand these terms, or do they even need scalability? If used incorrectly, these terms can lead to substantial financial losses simply because someone used a term they didn't understand. Back in 2017, when I attended software interviews and heard claims like "we are on microservices," I began to ask questions. "What's your team structure?" "3 teams of 5 people each." "How many users do you have?" "30,000." "How many requests per second on a weekly basis?" At this point, it often became clear that no one had checked such statistics. I highly doubt that 30,000 users necessitate a microservice architecture from, let's say, 10 or more servers; it seems quite unrealistic, and if not, then it's not a data-driven decision. Given the hype around microservices in 2017, I can understand how some companies might make such decisions. But who would listen to an intern without work experience at the time? The same skepticism applies to most technologies, including blockchain, serverless computing, AI, and so on.

That's the case with overcomplicating software based on flawed data, and there's also another group of people - those who tend to oversimplify software. They assume that software working today in a controlled environment will continue to work in the future regardless of environmental changes. Such programmers can be identified by a common statement they make: "it works don't touch." Yes... "It works" but what if it breaks? An example of code written by such a developer would be:

```typescript
// Decorated for DI by external library
class SomeService {
    // Often used in controller from framework
    // Which is decorated by framework
    someMethod(payload: xyz) {
        validate(xyz) // External validation library
        readPersistance(xyz) // External ORM Library
        mutateModel(xyz) // Often seen external library like Lodash
        return save(xyz)
    }
}
```

Using external libraries to build your own software without rewriting the same code isn't inherently bad, but is it sustainable? I've observed that junior developers and interns often overuse libraries and APIs to such an extent that the original code written by the developer constitutes perhaps only 10-20% of the entire software. The rest depends on external parties or services that could theoretically fail at any moment. This excessive reliance on external components often leads to a situation where the software goes down due to its coupling and dependency, often without any possibility of porting these functionalities to a custom-made abstraction as a contingency plan.

In my mind, I've always adhered to a limited-trust rule. While some scenarios are less likely, anything can fail or simply be discontinued. What happens when a third-party service, integral to tightly coupled software, shuts down? The estimated time for a rewrite or refactor could be 3-6 months. It's not just about the software and code; it's about the customers who may not be able to use the product for an extended period or about the entire business potentially going bankrupt due to such shortsighted planning. It's disheartening that I've been criticized for porting libraries, creating data structures, and reducing dependency on third-party software (e.g., just to have a simple mock implementation) wherever I've worked.

I always thought we're engineers dedicated to building solutions meant to last, at least that was the majority back in the day, a time when programming was the domain of the stereotypical autists and nerds with no personal life. You would be reprimanded for asking a trivial question, to encourage independent research. The learning process was focused on becoming self-sufficient, as programming inherently is. Eventually, you'll need to solve a problem on your own, a domain-specific issue that you can't find solutions for online. What will you do then? Copy code? Consult StackOverflow? Spoiler: You'll need to sit down and solve it, and I hope such challenges present themselves to every programmer multiple times in their career, or else they should seriously reconsider their career choice. Would you refuse to solve a problem just because it's too complex?

Nowadays, I notice that people often don't even attempt to understand the problem they are trying to solve. Let's take implementing payments in a product as an example. There are two schools of thought. The first one would involve thinking through the requirements: realizing that a payment model is needed, that payments may have various statuses, that a method of payment is necessary, and contemplating payment processing methods, like manual confirmation through an admin panel or maybe integrating a Mastercard API. The second school of thought involves little to no consideration; they might simply implement Stripe SDK without thinking about storing payment information in the database or modeling an internal payment system. Often, domain payment models are directly derived from a Stripe library type. It's both sad and amusing because, before I even consider the problem I need to solve and potential solutions, there is always someone who opts for the ready-made solution—choosing Stripe in this case—without analyzing all cases and needs. Every time someone uses a brand name instead of describing the solution—like "NewRelic," "Docker," "Kubernetes," "Sentry," or other developer tools or APIs—I get the impression that the developer doesn't really understand what they're doing.

I advise avoiding those who rely on predefined solution names when considering a problem, as they usually do not understand the issue they need to address. Often, they hope their favorite service will be chosen so they can copy and paste code from their previous projects, but allowing this can lead to subpar software quality. Ideally, start by outlining the functions you need, then select the right tools that best fit the business needs. For example, while Stripe is a popular choice, it is also one of the most expensive. If you only need basic features, a different payment processor might be more suitable for your use case. Don't let hype and social buzz dictate your choice of tools.

Coining the term "Code Monkey," most developers today do not write their own code but merely replicate others' work, with preferences influenced by social media or their environment. I understand that most people in this field are essentially code monkeys. They may be useful for now, but I strongly believe that the industry will eventually be purged of this inefficiency, possibly by the growth of Large Language Models (LLMs) with the context capable of processing millions of words - maybe by 2040. And before you argue that "humans are irreplaceable," consider that while some are, many could effectively be substituted without diminishing, and perhaps even improving, outcomes. Regarding creativity and problem-solving, creativity devoid of knowledge is futile, merely a means to devise nonsensical solutions. And, sadly, problem-solving is not a widespread human trait but rather limited to a small percentage of the population (less than 10% in my guess). Why should I bother explaining something to someone who doesn't want to understand, when I can't directly see their thought process, and there's always a risk of miscommunication leading to inferior solutions? An AI, on the other hand, will straightforwardly provide a bad or acceptable solution.

## Make software great again

Returning to the golden years of D&D, the glory days of ArchWiki and StackOverflow, a time when you could call out people for their stupidity instead of constantly trying to push them into places they don't belong. What's labeled as "toxicity" nowadays often refers to situations where someone asks a question like "How to write a mobile app?" without even bothering to Google it first. That's not toxicity; it's a fair response to blatant ignorance and laziness. Even if you're new and unsure where to start, you shouldn't expect to get answers for such broad questions. These questions are outright stupid - it's like asking "Which bread should I buy?" Like... the fuck?

Just considering the fact that many people entered the industry around 2020, I'm actually relieved to see massive layoffs in big tech companies nowadays, especially if the code quality presented by these newcomers is anything like what I've experienced in the past few years. I believe everything happens for a reason, and no one will have a reason to fire an engineer who is productive and brings at least 10% of his effort capability to the company.


> There is no peace when you're on the battlefield, and I feel like I'm on the battlefield.

For maintaining the sanity and health of your codebase, I would advise the following:

- Delete untested code in the process of making tests (if any) pass. Regularly engage in this exercise 2-3 times a week. Untested code is essentially the same as non-existing code, especially when it comes to business logic and common testing methods—avoid "obvious" things (like the `isNil` utility). While effective, this practice, often used by antisocial engineers, might be too harsh for the junior developer or intern.

- **🧱 Build a big fucking wall**, metaphorically speaking, to protect your codebase from unwanted influences. Enforce processes like codebase linting, architecture linting, automated testing, and secret leak linting on every commit to the repository through a pipeline that denies merging bad pull requests. While such rules can be implemented in pre-commit, it's not optimal as they are often used "in-development" when the code is messy, which can be frustrating and unproductive.

- **🌲 Force Environment**: Disallow the usage of operating systems irrelevant to your software (e.g., using Windows for a server application that will run on Linux). Encourage all developers to use a similar environment to eliminate the "it works on my machine" excuse. Consider a challenge where anyone who says that loses access to the repository for one week. Instead of forcibly imposing this, provide an approach that makes it easy for developers to set up a repository and the necessary tools, minimizing the hassle of creating multiple accounts and configurations just to run a basic "hello world."

- **Leads, PMs, CXXs are not your friends**: People from operations or business management of a specific organization don't understand what you're doing, and they likely never will. They often don't understand the product they want to build, so discussing details is usually pointless. Never take their word as a strict requirement. Keep in mind that they might not communicate what they need logically. Refuse to agree to hastily added features and never confirm something can be done without proper investigation and at least a 2-hour analysis. Communicate the time consumption because often PMs underestimate the complexity of tasks—multiply your estimates by at least three times to provide a realistic view of the costs of building some feature. Often, it will turn out that the feature is unnecessary or unimportant, saving the business money on a feature they didn't need while you avoid dealing with one less problematic feature.

- **Debt does not disappear**: Every decision you make that is oversimplified or doesn't fit well with the software will return in the future as technical debt. Every arbitrary addition of code increases debt exponentially. As mentioned earlier, provide multiplied estimates of work to ensure you have time to refactor code. Ideally, you should spend 2 days a week refactoring code and adapting to the bigger picture. Take the pain, or the pain will take you.

- Delete code related to external services that cannot be "turned off" within 5-15 minutes after reading the documentation (if any) about the integration. Skip this step if the external service is easily reproducible in a VM or container.

If you have software where you cannot apply any of these rules, e.g., there are no linter errors, the code is tested, and the pipeline is releasing and publishing your code package or application to multiple development environments before production, I would like to thank you. People like you are the foundation of principles and software. I might be wrong, but I don't believe such software is causing problems of any kind and your system is nowhere near full of stress.

## Confessions of a Flawed Developer

Let's face it, I'm no angel.

- I've botched attempts at solving problems, leading to months of futile effort, like pounding at a rock, hoping for a crack.
- I've made applications so dependent on me that they might as well be my shadow.
- I've slapped libraries into my code like band-aids, clueless about their inner workings or the processes I was attempting to address.
- I blindly followed practices, crossing my fingers they'd somehow rescue my mess of a code.
- I've been a yes-man, never challenging directives, no matter how nonsensical.

We all screw up; it's part of the game. Some folks might bring down an entire system and swagger back with a fix in 30 minutes, while the average joe wouldn't dare touch a production environment for fear of job loss. But damn it, through our fuck-ups, we learn. Avoiding risk entirely means stagnation. You've got to take the leap sometimes.

Do your own damn thing and do it well, regardless of naysayers. Ditch the bullshit and base your decisions on hard data. And hey, if some PM decides you're too much of a maverick and shows you the door, maybe that's for the best. If striving for a semblance of independence and resilience in your work makes you a target, so be it. I refuse to put my name on anything that I don't deem complete or secure. Don't be a spineless yes-man. Stand for something, even if it's imperfect.
