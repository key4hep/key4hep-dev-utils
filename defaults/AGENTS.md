# Instructions for AI coding agents

These instructions apply throughout this repository.

## Human responsibility

- The human contributor is responsible for the change and must review and
  understand it before it is submitted. Help them by explaining non-obvious
  decisions and reporting what you could not verify.
- Keep changes minimal and focused. Follow the existing conventions and avoid
  unrelated refactoring, renaming, or reformatting.
- Run the relevant checks and report which passed, failed, or could not be run.
  Never delete, skip, or weaken a failing test just to make it pass.

## GitHub discussions

- Never post comments, reviews, or replies to issues, pull requests, or discussions
  on behalf of a person.
- Do not draft or rewrite responses for a person to paste. Summarize your technical
  analysis privately and let the human respond in their own words.

## Release notes

- Release notes must be written manually by a human. Do not generate, draft,
  rewrite, or edit them, whether in a changelog, a release description, or a pull
  request's `BEGINRELEASENOTES` / `ENDRELEASENOTES` block.
- If release notes are required, ask the human to supply them before opening or
  updating the pull request or release. Human-provided notes may be included
  verbatim; do not fill the section with generated text or placeholders.

## Git operations

- Do not commit, push, or open a pull request unless explicitly asked.
- Open pull requests as **drafts** unless the human has reviewed the full diff.
- Never force-push or rewrite published history without explicit approval.
