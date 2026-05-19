# /onboard — New Team Member Orientation

Generate an architecture summary and orientation guide for someone joining the project.

## What this does

Reads the codebase and produces a practical "here's how everything works" guide for a new developer on the team.

## Steps

```
Run: find src/ -type f -name "*.js" | head -40
Run: cat package.json
Run: cat README.md
Run: git log --oneline -20
```

Then explore the key folders to understand the structure.

## What to produce

### 1. Project overview (2-3 sentences)
What does this app do? What's the tech stack?

### 2. How to get started
- Clone, install, run locally
- Environment variables needed (check `.env.example`)
- How to run tests

### 3. Folder map
Explain what each folder does in plain English.

```
src/
  routes/      → <explain>
  models/      → <explain>
  middleware/  → <explain>
  config/      → <explain>
tests/
  unit/        → <explain>
  integration/ → <explain>
```

### 4. The 5 most important files to read first
List them with a one-line reason for each.

### 5. How we work
- Branching strategy
- How to make a PR
- Commit message format
- Who to ask about what

### 6. Common tasks and how to do them
- Add a new route
- Add a new model
- Write a test
- Run the linter

### 7. Things to be careful about
- Known gotchas
- Things that have broken before
- Areas of the code that are fragile

## Format

Make this readable. Use headers, short paragraphs, and bullet points. Imagine you're writing it for someone who is smart but new to this specific codebase.
