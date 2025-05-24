---
title: 'Works on my machine'
description: ''
pubDate: 'Dec 25 2023'
heroImage: '/blog-placeholder-3.jpg'
tags: ['rant', "software-engineering"]
collection: 'software-is-hopeless'
order: 1
---

Every time I hear this statement, I want to flatline the person who said it due to the ignorance it displays.

It's too easy to blame the user, but in reality, it's usually not their fault - if software you ship behaves differently on "your" machine and machine of end-customer (or target environment) - maybe you should consider at least checking out if it really works before saying it works.

I always ask about a containerized environment or some VM so I can really see if it "works on your machine," and suddenly there is none of those - it's some local copy off main which isn't even available to others but yeah... "it works".

Docker been released in fucking 2013, and around 2017 (at least I felt like) Nix was popularized for development environments - it's been 8 years since then and you all still using excuse that been shitty even in 2013 as you could run VM environments.

Just fucking say you don't have intention to ship it and that's it, or if you can't shut your stupid mouth.
