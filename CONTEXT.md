# FitScorer

A personal tool that compares a job posting against the user's own career profile and reports how well they fit it, where the gaps are, and how to reposition around them.

## Language

**Profile**:
The user's de-identified, structured record of their own background — education, skills, work experience, certifications, and languages — maintained as a single JSON document and treated as the ground truth the user's fit is judged against.
_Avoid_: CV, resume, skills list (too narrow — a Profile is the whole structured record, not just skills)

**Skill Entry**:
A single named capability in the Profile's skills section, carrying a proficiency level and a category.
_Avoid_: Skill (ambiguous between "Skill Entry in the Profile" and "Required Skill on a JobPosting" — always qualify which)

**Experience Entry**:
A single role in the Profile's work-experience section: a role title, a duration, and a genericized description that serves as evidence for skill matching but never names the employer.
_Avoid_: Job, position

**JobPosting**:
The pasted, untrusted text of an external job advertisement, and the structured data extracted from it (role title, required skills, preferred skills, seniority level).
_Avoid_: Job, listing, posting (alone — always "JobPosting" as the term of art)

**Required Skill**:
A must-have skill extracted from a JobPosting. Distinct from a Preferred Skill (nice-to-have) and from a Profile's Skill Entry.
_Avoid_: Skill (unqualified)

**Skill Verdict**:
The judgment — match, partial, or missing, with a short rationale — of whether the Profile satisfies one Required Skill from a JobPosting. Produced by reading the Profile as a whole (not just the skills section), so an Experience Entry or Education Entry can serve as evidence even when the skill isn't listed verbatim.
_Avoid_: Match, result, score (a Skill Verdict is not itself the score — it's one input to it)

**Fit Score**:
The single numeric result for how well a Profile fits a JobPosting, computed deterministically by aggregating all Skill Verdicts for that JobPosting. Never produced directly by an LLM.
_Avoid_: Match score, result

**Repositioning Suggestion**:
Narrative advice for how the user could present their existing Profile to better fit a JobPosting's gaps, generated from the already-computed Skill Verdicts and Fit Score. It narrates a gap that has already been determined — it does not determine the gap itself.
_Avoid_: Recommendation, advice (alone)

**Session**:
One continuous use of the app: a Profile loaded once, followed by one or more JobPostings pasted and scored in sequence, with each result kept in the running Session History until the app is closed.
_Avoid_: Run (a Run is one JobPosting scored; a Session is the whole sequence)

**Session History**:
The running, in-memory record of every JobPosting scored during the current Session, shown as a comparison table the user can revisit. Lost when the Session ends unless individually saved.

**Report**:
The persisted, user-triggered export of one scored JobPosting's full result (Fit Score, Skill Verdicts, Repositioning Suggestion) to a Markdown file. Distinct from the Session History, which is in-memory and ephemeral.
_Avoid_: Export, save file
