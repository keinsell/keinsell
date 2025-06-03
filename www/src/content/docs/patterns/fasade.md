---
title: "Facade"
description: "A structural design pattern that provides a simplified interface to a complex subsystem"
category: "structural-patterns"
implementations: ["preferences"]
tags: ["abstraction", "encapsulation", "typescript", "beginner"]
relatedPages: ["patterns/adapter", "patterns/proxy"]
sidebar:
  hidden: false
  order: 1
  label: "Facade Pattern"
lastModified: 2025-01-03
---

# Facade

A structural design pattern that provides a simplified interface to a complex subsystem.

## Overview

The Facade pattern hides the complexities of the system and provides an interface to the client using which the client can access the system. This pattern involves a single class which provides simplified methods required by client and delegates calls to methods of existing system classes.

## When to Use

- You want to provide a simple interface to a complex subsystem
- There are many dependencies between clients and implementation classes
- You want to layer your subsystems

## Implementation

See the [preferences implementation](/docs/implementations/preferences/) for a practical example.
