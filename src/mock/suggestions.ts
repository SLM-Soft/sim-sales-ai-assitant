const suggestionByOption: Record<string, string[]> = {
  general_llm: [
    'Summarize the latest product updates for SLM.',
    'Give me three ideas to improve customer onboarding.',
    'Draft a quick status update for stakeholders.',
  ],
  project_analysis: [
    'What gaps do you see in the provided dataset?',
    'List the top 3 insights we can pull first.',
    'What early risks should we check in the data?',
  ],
  cost_optimization: [
    'Where are the quick wins to cut costs?',
    'How can we reduce cloud spend safely?',
    'Which processes look most expensive to automate?',
  ],
  sales: [
    'Show me your case studies.',
    'Share AI case studies in healthcare.',
    'What recent wins can we pitch to the client?',
  ],
};

export { suggestionByOption };
