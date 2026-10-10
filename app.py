import os
from dotenv import load_dotenv
import streamlit as st
from research import fetch_sources, validate_request

load_dotenv()
st.set_page_config(page_title='ContentCrew', page_icon='✍️', layout='wide')
st.title('✍️ ContentCrew')
st.caption('Research → outline → key points → article or LinkedIn post')
st.info('Approved source: English Wikipedia introductory excerpts. Best for background topics; coverage of current events may be incomplete.')
with st.sidebar:
    st.header('Model connection')
    provider = st.selectbox('Provider', ['OpenAI', 'Ollama'], index=1 if os.getenv('LLM_PROVIDER', '').lower() == 'ollama' else 0)
    if provider == 'OpenAI':
        model = st.text_input('OpenAI model', os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
        entered_key = st.text_input('OpenAI API key (optional if configured in .env)', type='password')
        api_key = entered_key or os.getenv('OPENAI_API_KEY', '')
        base_url = ''
        st.caption('API billing is separate from a ChatGPT subscription. The key is not included in downloads.')
    else:
        model = st.text_input('Ollama model', os.getenv('OLLAMA_MODEL', 'llama3.1:8b'))
        base_url = st.text_input('Ollama URL', os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
        api_key = ''
        st.caption('Use a model capable of tool calling and structured output. Run ollama list to check installed models.')
    st.caption('Requests and source excerpts go to the selected LLM provider. Research uses Wikipedia online in both modes.')
with st.form('request'):
    topic = st.text_input('Topic', placeholder='How data quality improves healthcare analytics', max_chars=300)
    audience = st.text_input('Audience', value='Professionals interested in data and healthcare', max_chars=150)
    c1, c2 = st.columns(2)
    style = c1.selectbox('Output format', ['Article', 'LinkedIn-style post'])
    words = c2.slider('Target word count', 150, 1200, 500, 50)
    submitted = st.form_submit_button('Research and write', type='primary')
if submitted:
    st.session_state.pop('result', None)
    try:
        validate_request(topic, audience)
        from workflow import make_llm, run_crew
        llm = make_llm(provider, model, api_key, base_url)
        with st.status('Running the research and writing workflow…', expanded=True) as status:
            st.write('Retrieving approved source excerpts…')
            sources = fetch_sources(topic.strip())
            st.write(f'Found {len(sources)} sources. Executing the two-agent Crew…')
            result = run_crew(topic.strip(), audience.strip(), style, words, llm, sources)
            st.session_state.result = result
            status.update(label='CrewAI execution complete', state='complete', expanded=False)
    except ValueError:
        st.error('Check the topic/audience lengths, model name and API key. Research may also have returned no usable sources; try a more specific topic.')
    except Exception:
        # Provider exceptions can contain credentials or sensitive request bodies.
        st.error('The workflow could not complete. Check your connection, API credits, model name and tool/JSON support, then retry. No draft was produced.')
if 'result' in st.session_state:
    r = st.session_state.result
    draft = r['draft']
    tabs = st.tabs(['Final content', 'Outline & key points', 'Sources & research', 'CrewAI execution result'])
    with tabs[0]:
        if draft:
            st.subheader(draft['title'])
            st.markdown(draft['content'])
            if draft['limitations']:
                st.warning('Evidence limitations: ' + ' '.join(draft['limitations']))
            content = '# '+draft['title']+'\n\n'+draft['content']
        else:
            st.warning('Structured output was unavailable. The raw CrewAI result is shown below.')
            st.markdown(r['raw'])
            content = r['raw']
        content += '\n\n## Sources\n' + '\n'.join(f"- [{s['id']}] {s['title']}: {s['url']}" for s in r['sources'])
        st.download_button('Download Markdown', content, 'contentcrew_draft.md', 'text/markdown')
    with tabs[1]:
        if draft:
            st.subheader('Outline')
            for i, item in enumerate(draft['outline'], 1):
                st.write(f'{i}. {item}')
            st.subheader('Key points')
            for item in draft['key_points']:
                st.markdown('- '+item)
        else:
            st.info('See the raw result for the outline and key points.')
    with tabs[2]:
        for s in r['sources']:
            with st.expander(f"[{s['id']}] {s['title']}"):
                st.link_button('Open source', s['url'])
                st.text(s['excerpt'])
        st.subheader('Researcher’s task output')
        st.markdown(r['research'])
    with tabs[3]:
        st.success('Crew.kickoff() completed')
        st.text(r['raw'])
        st.caption('Usage: '+r['usage'])
        if draft:
            st.json(draft)
