class createMeetAgent:
    def __init__(self):
        pass
    
    def create_meet(self, state):
        print("Reunião foi criada com sucesso")
        return {"message": state["message"], "answer": "Horario marcado! Obrigado por escolher a nossa Barbearia!"}
    

class RescheduleMeetAgent:
    def __init__(self):
        pass
    
    def reschedule_meet(self, state):
        print("Reunião foi reagendada com sucesso")
        return {"message": state["message"], "answer": "Reunião foi reagendada com sucesso"}
    

class DeleteMeetAgent:
    def __init__(self):
        pass
    
    def delete_meet(self, state):
        print("Reunião foi cancelada com sucesso")
        return {"message": state["message"], "answer": "Reunião foi cancelada com sucesso"}