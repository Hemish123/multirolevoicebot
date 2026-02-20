def resolve_prompt(template, agent_name, company_name):
    return template.system_prompt_template.format(
        agent_name=agent_name,
        company_name=company_name or ""
    )