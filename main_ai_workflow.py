from langgraph.graph import StateGraph, END



class AgentWorkFlow:

    def __init__(self,state,chatbot,validate_agent,create_meet,reschedule_meet,delete_meet):
        self.state = state
        self.chatbot = chatbot
        self.validate_agent = validate_agent
        self.create_meet = create_meet
        self.reschedule_meet = reschedule_meet
        self.delete_meet = delete_meet
        pass

    
    def validate_params(self,state):
        print(state)
        if state["flag_use_tool"] and state['valid_params'] and state['tool_type'] == 'create_meet':
            print('create_meet')
            return 'creating_meet'
        if state["flag_use_tool"] and state['valid_params'] and state['tool_type'] == 'reschedule_meet':
            print('reschedule_meet')
            return 'rescheduling_meet'
        if state["flag_use_tool"] and state['valid_params'] and state['tool_type'] == 'delete_meet':
            print('delete_meet')
            return 'deleting_meet'


    def validate_params_init(self,state):
        if state["flag_use_tool"]:
            print('validating')
            return "validating"
        print("no_tool_needed")
        return "no_tool_needed"
    

    def build_graph(self):
        graph_builder = StateGraph(self.state)
        graph_builder.add_node("chatbot",self.chatbot.call_chat)
        graph_builder.add_node("validate",self.validate_agent.call_chat)
        graph_builder.add_node("create_meet",self.create_meet.create_meet)
        graph_builder.add_node("reschedule_meet",self.reschedule_meet.reschedule_meet)
        graph_builder.add_node("delete_meet",self.delete_meet.delete_meet)

        graph_builder.set_entry_point("chatbot")

        graph_builder.add_conditional_edges("chatbot", self.validate_params_init,{"validating": "validate","no_tool_needed":"__end__"})
        graph_builder.add_conditional_edges("validate", self.validate_params,{"creating_meet": "create_meet","rescheduling_meet": "reschedule_meet","deleting_meet": "delete_meet"})

        graph_builder.add_edge("create_meet", END)
        graph_builder.add_edge("reschedule_meet", END)
        graph_builder.add_edge("delete_meet", END)

        graph = graph_builder.compile()

        return graph
