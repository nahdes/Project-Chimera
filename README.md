# Tenx MCP Analysis - Documentation

**Date:** February 2, 2026  
**IDE:** VS Code  
**Agent:** GitHub Copilot

---

## What I Did

Created a comprehensive rules file (`copilot-instructions.md`) to guide GitHub Copilot's behavior. The goal was to align the AI agent with professional development practices.

### Research

- Studied Boris Cherny's workflow approach
- Reviewed community best practices for AI agent configuration
- Examined official documentation (GitHub Copilot, TypeScript, React)

### Key Sections Added

**1. Project Context**  
Defined tech stack and project phase to give agent immediate context.

**2. Core Principles**  
Established priority hierarchy: Correctness → Security → Maintainability → Performance

**3. Workflow Pattern: Plan → Implement → Verify**  
Required three-phase approach for every task to prevent rushing to code.

**4. Coding Standards**  
Specific rules for TypeScript, naming, function size, code quality with DO/DON'T examples.

**5. Documentation Requirements**  
Mandatory JSDoc comments with parameters, returns, exceptions, and examples.

**6. Testing Approach**  
Required unit tests, integration tests, and edge case coverage.

**7. Error Handling**  
Strict patterns: try-catch for async, custom errors, comprehensive logging.

**8. Communication Guidelines**  
How agent should respond: plan first, explain WHY, show trade-offs, flag assumptions.

**9. Personal Preferences**  
Specific choices like composition over inheritance, hooks over HOCs.

**10. Learning Loop**  
Section to track repeated corrections and improve over time.

**11. Security & Quality Checklists**  
Pre-commit verification lists for code quality and security.

**12. Example Interactions**  
Concrete examples of good agent responses.

---

## What Worked

### Structured Workflow (Plan → Implement → Verify)

Requiring the agent to propose a plan first dramatically improved code quality. The agent now breaks down tasks, identifies risks, and waits for confirmation before coding. This prevents issues before they're written.

### Code Examples (DO vs DON'T)

Including concrete examples transformed output quality. The agent consistently follows patterns when shown exactly what to do versus abstract descriptions.

### Documentation Requirements

Requiring JSDoc comments led to self-documenting code and made the agent consider edge cases more carefully.

### Testing Guidelines

The agent now proactively suggests test cases, identifies edge cases, and recommends verification commands.

### Error Handling Patterns

By providing a specific pattern, the agent now always includes proper try-catch blocks, context logging, and custom error classes.

### Communication Style

Responses became concise, actionable, and focused on explaining WHY rather than just WHAT. The agent shows trade-offs between approaches.

### Security Checklist

The agent proactively validates inputs, flags potential vulnerabilities, and reminds about authentication checks.

### Project-Specific Rules

Specifying conventions (use Zod, all API calls through apiClient) ensures consistency without needing to repeat preferences.

---

## What Didn't Work

### Too Much Complexity

Initial rules file was too long and detailed. The agent became confused, missed important guidelines, and responded slower.

**Solution:** Reduced length, consolidated rules, created clear hierarchy.

### Overly Prescriptive Formatting

Rigid formatting requirements ("exactly 3 bullet points", "max 10 lines") made responses robotic and sacrificed clarity.

**Solution:** Shifted to principle-based: "Be concise but clear" with flexibility based on context.

### Learning Loop Not Automatic

The agent doesn't automatically update the rules file or retain learning across sessions.

**Solution:** Manual updates after sessions where repeated corrections occur.

### Context Window Limits

With large files, agent sometimes "forgot" rules and fell back to default behavior.

**Solution:** Work on smaller tasks, explicitly reference specific rules in prompts when needed.

### Ambiguous Rules

Vague rules like "write good tests" led to inconsistent interpretation.

**Solution:** Made rules concrete with measurable criteria and examples.

### Conflicting Rules

Rules sometimes contradicted ("keep functions under 30 lines" vs "comprehensive error handling").

**Solution:** Added priority hierarchy where security and correctness always trump brevity.

---

## Insights Gained

### Rules Fundamentally Change Agent Behavior

The AI agent's behavior is highly malleable. With custom rules, it transforms from a basic code generator to a thoughtful development partner that plans, implements systematically, and verifies its work.

### Concrete Examples Beat Abstract Principles

Rules with code examples are followed exponentially better than abstract descriptions. Show the agent exactly what you want rather than describing it.

**Example:**

```typescript
// ✅ DO: Include this pattern
async function fetch(id: string): Promise<User> {
  try { ... } catch (error) { logger.error(...); throw new CustomError(...); }
}

// ❌ DON'T: Show what to avoid
async function fetch(id) {
  return api.get('/users/' + id).then(r => r.data);
}
```

This produces exponentially better code than saying "use proper error handling."

### Structure Reduces Cognitive Load

Organizing rules hierarchically (Core Principles → Standards → Preferences) makes both the AI and my own thinking more systematic. Clear priority helps resolve conflicts.

### Plan → Implement → Verify is Transformative

This three-phase workflow catches issues before they're coded, reduces debugging time significantly, and forces systematic thinking. Slowing down to plan actually speeds up overall development.

### Rules Create Shared Mental Model

The rules file acts as a contract between human and AI. It aligns expectations about what "good code" looks like, reducing friction and making collaboration natural.

### Specificity Matters

More specific rules get better compliance:

- Vague: "Write maintainable code" → inconsistent
- Specific: "Functions under 30 lines" → better
- Concrete example: Shows exact pattern → best

### Iteration is Essential

Rules files aren't one-time setups. They evolve through testing, refinement, and learning from real usage. Each iteration produces exponentially better results.

### Context-Dependent Application

Different tasks benefit from different rule emphasis:

- New features: Plan → Implement → Verify critical
- Bug fixes: Error handling patterns most important
- Refactoring: Code quality rules dominate

### Rules Encourage Systematic Thinking

With structured rules, the agent proactively considers edge cases, error conditions, performance implications, and security concerns it would otherwise skip.

### Learning Requires Human Participation

The agent learns within sessions but doesn't persist across them. True improvement requires manually updating rules based on repeated corrections.

### Rules Enable Meaningful Delegation

Good rules transform the agent from a code completion tool to a collaborator. You can confidently delegate feature implementation while focusing on architecture and creative problem-solving.

### Balance Prescription with Flexibility

Use imperative language ("must") for critical rules like security. Use suggestive language ("should", "prefer") for preferences. Context matters more than rigid compliance.

---

## Summary

### Key Takeaways

**Most Impactful Changes:**

1. Concrete examples produce exponentially better code than abstract principles
2. Plan → Implement → Verify workflow transforms development quality
3. Rules create shared mental model between human and AI
4. Iterative refinement essential - living document, not one-time setup
5. Balance prescription (security, errors) with flexibility (preferences)

### Recommended Approach

**Starting Fresh:**

- Begin with 10-15 core rules with examples
- Test with real tasks, observe results
- Add/refine based on what works
- Structure: Core Principles → Standards → Preferences

**Critical Patterns:**

- Always show DO vs DON'T code examples
- Require planning before implementation
- Make security and error handling rigid
- Keep preferences flexible

**Continuous Improvement:**

- Test rules deliberately
- Note repeated corrections
- Update rules file manually
- Treat like code - refactor and optimize

---

**Document Version:** 1.0  
**Last Updated:** February 2, 2026
