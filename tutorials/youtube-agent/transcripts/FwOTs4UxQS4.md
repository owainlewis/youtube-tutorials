# AI Agents, Clearly Explained

Channel: Jeff Su
Views: 3.5M
Source: https://youtube.com/watch?v=FwOTs4UxQS4

---

AI. AI. AI. AI. AI. AI. You know, more agentic. Agentic capabilities. An AI agent. Agents. Agentic workflows. Agents. Agents. Agent. Agent. Agent. Agent. Agentic. All right. Most explanations of AI agents is either too technical or too basic. This video is meant for people like myself. You have zero technical background, but you use AI tools regularly and you want to learn just enough about AI agents to see how it affects you. In this video, we'll follow a simple one, two, three learning path by building on concepts you already understand like chatbt and then moving on to AI workflows and then finally AI agents. All the while using examples you will actually encounter in real life. And believe me when I tell you those intimidating terms you see everywhere like rag, rag, or react, they're a lot simpler than you think. Let's get started.

Kicking things off at level one, large language models. Popular AI chatbots like CHBT, Google Gemini, and Claude are applications built on top of large language models, LLMs, and they're fantastic at generating and editing text. Here's a simple visualization. You, the human, provides an input and the LLM produces an output based on its training data. For example, if I were to ask Chachi BT to draft an email requesting a coffee chat, my prompt is the input and the resulting email that's way more polite than I would ever be in real life is the output. So far so good, right? Simple stuff. But what if I asked Chachi BT when my next coffee chat is? Even without seeing the response, both you and I know Chachi PT is gonna fail because it doesn't know that information. It doesn't have access to my calendar. This highlights two key traits of large language models. First, despite being trained on vast amounts of data, they have limited knowledge of proprietary information like our personal information or internal company data. Second, LLMs are passive. They wait for our prompt and then respond. Right? Keep these two traits in mind moving forward.

Moving to level two, AI workflows. Let's build on our example. What if I, a human, told the LM, "Every time I ask about a personal event, perform a search query and fetch data from my Google calendar before providing a response." With this logic implemented, the next time I ask, "When is my coffee chat with Elon Husky?" I'll get the correct answer because the LLM will now first go into my Google calendar to find that information. But here's where it gets tricky. What if my next follow-up question is, "What will the weather be like that day?" The LM will now fail at answering the query because the path we told the LM to follow is to always search my Google calendar, which does not have information about the weather. This is a fundamental trait of AI workflows. They can only follow predefined paths set by humans. And if you want to get technical, this path is also called the control logic.

Pushing my example further, what if I added more steps into the workflow by allowing the LM to access the weather via an API and then just for fun use a text to audio model to speak the answer. The weather forecast for seeing Elon Husky is sunny with a chance of being a good boy. Here's the thing. No matter how many steps we add, this is still just an AI workflow. Even if there were hundreds or thousands of steps, if a human is the decision maker, there is no AI agent involvement.

Pro tip: retrieval augmented generation or rag is a fancy term that's thrown around a lot. In simple terms, rag is a process that helps AI models look things up before they answer, like accessing my calendar or the weather service. Essentially, Rag is just a type of AI workflow.

By the way, I have a free AI toolkit that cuts through the noise and helps you master essential AI tools and workflows. I'll leave a link to that down below.

Here's a real world example. Following Helena Louu's amazing tutorial, I created a simple AI workflow using make.com. Here you can see that first I'm using Google Sheets to do something. Specifically, I'm compiling links to news articles in a Google sheet. And this is that Google sheet. Second, I'm using Perplexity to summarize those news articles. Then using Claude and using a prompt that I wrote, I'm asking Claude to draft a LinkedIn and Instagram post. Finally, I can schedule this to run automatically every day at 8 a.m. As you can see, this is an AI workflow because it follows a predefined path set by me. Step one, you do this. Step two, you do this. Step three, you do this. And finally, remember to run daily at 8 am.

One last thing, if I test this workflow and I don't like the final output of the LinkedIn post, for example, as you can see right here, uh, it's not funny enough and I'm naturally hilarious, right? I'd have to manually go back and rewrite the prompt for Claude. Okay? And this trial and error iteration is currently being done by me, a human. So keep that in mind moving forward.

All right, level three, AI agents. The key shift here is who controls the decision-making. In workflows, humans define every step. With agents, the AI becomes the decision maker. It can observe results, reason about what to do next, and take action autonomously.

ReAct (Reasoning and Acting) is a popular framework for building agents - the AI reasons about what to do, takes an action, observes the result, and loops until the goal is achieved.

Summary of the three levels:
- Level 1: LLMs - great at text, but passive and limited knowledge
- Level 2: AI Workflows - add tools, but follow human-defined paths  
- Level 3: AI Agents - AI controls decisions and adapts dynamically
