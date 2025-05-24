---
title: 'software architecture is not in folders'
description: 'Your architecture should explain itself.'
pubDate: 'March 01 2023'
heroImage: '/blog-placeholder-3.jpg'
tags: ['rant', 'software-architecture', 'harmful']
collection: 'software-architecture'
order: 1
---

TL;DR: Architectural Cargo-Culting, Decision-Making Without Reasoning, Blind Authority.

I have seen there is a major misunderstanding between people what software architecture is and what isn't, there are people who believe (there's no other word for it) that organizing files in a specific way makes software architecture good while structure they have choose on day 0 have introduced way more trouble than it solved - yet will argue it's a "good practice".

**Fuck your good practices, your architecture and fuck you after all.**

I don't really care if somebody will push a non-critical bug into codebase, but you are worst of the worst kind of animals, you will multiply effort needed to handle codebase by at least 10x - while by my experience, you tend to pretend you know what's where but even in your own architecture you all are lost as fuck - no wonders, you should not be given responsible task at the first place.

When I see directories organized (to be clear, in module that could be enclosed as 10 lines in controller) in a way where sum of import/export lines is higher than size of module itself - you fucked up, I don't care who said to you that you should do this that way, how much you paid for course or how famous person who said that is - it's fucking retarded and if you cannot reason why it's this way not another - you shouldn't have any decision-making power over codebase.

**Presented situation had it's own place in real world, please don't try this when psychopaths like me are around because you will not make it to next christmas \s**

## The "Clean" Way

Let's define what *clean* means to me, it means that no unnecessary pieces are visible for an eye, it's what makes my room clean and my code clean. When it comes to "clean" architecture done by *architecture astronauts* it always tend to end way like this.

```
- src
  - interfaces
    - http
      - rest
        - controllers
          - product_controller
  - services
    - product
      - product_service
  - domain
    - product
      - value_objects
        - product_id
        - product_name
        - product_price
      - aggregates
        - product_aggregate
      - policies
        - minimal_price_policy
      - services
        - product_service
      - repositories
        - product_repository
      - use_cases
        - get_product_use_case
        - create_product_use_case
  - infrastructure
      - rest
        - restful_app
      - database
        - repositories
          - product_repository
        - entities
          - product_entity
  - utils
```

And sure... I can understand it pretty well as I know responsibilities of each layer, but this doesn't change the fact new-commers which most likely you want in healthly organization structure will get lost in this. Therefore I find it egoistic and more of a ego/cargo-driven than pragmatism-driven. You can even consider the fact you need a way more jumping through different files than it is for doing things same but in different way.

### Don't see a problem?

Just leave.
Log-off.
I don't know...
Do whatever you want just to make it that I will never met you again in my life.

## Mine (degenerated) architecture

Since, none of you onion/clean architecture fanatics was able to logically reason why organizing files in such way is implementation of architecture and doing it other way isn't - yet you agreed/leaned towards one option not another.

I don't say inspiring yourself by others is bad idea, you can do that if you are wise enough to understand that person from who you getting inspired is coming from different onthology and is operating on different facts/environment/constraints than you do - and if you could do that I would be not wasting my time complaining on shit like this

I inspired myself by #vertical-slice-architecture #clean-architecture and #package-by-feature - method presented is mix of everything, because foundation of software architecture is above everything adaptation to needs of business not adaptation of business to architecture like I have heard. How you can attend fucking course, finish it, have 10 years of experience yet say such fucking burden.

```
- e_commerce_repository
  - src
    - http
      - product
    - product
      - model
      - service
      - repository
    - db
      - orm
      - migration
```

I could as well start with following implementation when I would be developing application today.

```
- e_commerce_repository
  - http
  - product
  - db
```


### Imbecile-proof (at any time)

- We know what we're building, there's zero need for boilerplate directory structure that would "satisfy" implementation for any application - we know the application and we know that application aren't going to be rebuilt from scratch. Therefore there's no rational reason to use weird combination of `infrastructure` and `application` directory, also there is no reason of separating domain from service layer (even I understand them as same fucking thing).
- Once I enter repository and I see `http` I know what's there, name is self-explaining and it's top-level directory which have subjective meaning it's module containing group of things rather than just being a single thing. It's a matter of correct naming as `http.rest.route.v1.product` not `interfaces.http.rest.controllers.product_controller` which is "clean" but in reality is just shit by middle of the room.
  - Same goes with `db` and `db.orm.entity.product`/`db.repository.product`, it's reasonable to have all of the code related to database to have hmm... guess where... Yeah! In a fucking `db` directory!!! - Where you do shenigans in infrastructure directory, that doesn't often explain itself.
- Architecture is meant to be flexible and adaptable, not fixed. There is no rules standing you should do microservices because it's the most scalable method - when your team is monolithic you should go with monolith, architecture is about reflecting business not modeling business. Therefore, you start with simple `product` module which can just contain `update_product` function, and when building application [you can omit persistance ignorance rules if you are using orm, orm responsibility is to abstract away persistance ignorance to be able to use different databases.](https://x.com/keinsell_/status/1927129470604861506) Point is, you should not be so pro-active with abstractions and vertical layers, it leads to lasagna that is avoidable just by thinking in the process and reacting to issues as they happen instead brainlessly producing code.

### You don't understand "you"

- I don't give a shit what somebody else does, it's codebase where **I** will be handling problems and I don't want to make my job more complicated than it is already, and yeah - those who spent at code the least will be main source of noise.
- When **developer** says you **architect** is retarded, you should at least hear reasons about it, not like a kid assume others aren't as enlightened as you and cannot see brilance you have done - which lands in severe down syndrome diagnosis.
- Architecture aren't landing in files, it all lands in dependency structure which will never be reflected through files. Complicating your directory structure to force pattern you have learned is just fucking mid, complicating simple modules aren't worth it for one module that might be complicated, and even in this case first approach composes better.


## Disclaimer

Even through tone of post is sympthom of mental retardation, situation like this happen and purpose of this post is to show what gate-keeping have done to industry - especially gate-keeping done by retards for retards. I would like believe people just trolling, joking and messing around so they make decisions they make but it's not funny, it's not productive it's just copy and paste on positions where one is supposed to **lead** and **make decisions with real-world consequences** for other team-members, business or even affecting customers. You might find me toxic, be it - i don't give a shit... But if I am toxic (toxic style of communication doesn't make me toxic, same as your "professional" style of communication doesn't make you professional - let's be adults for a moment) and this isn't then I will just quit, there's no hope.

Please leave your environment if you are me from post, it will end horrible for you - as more you stay.
