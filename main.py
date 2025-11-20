from llm_client import ask_orion
from dispatcher import dispatch

print("=== Orion v0.1 conectado a Ollama ===")

while True:
    prompt = input("Escribí tu prompt para Orion:\n> ")
    call_data = ask_orion(prompt)
    
    if call_data['CALL']:
        result = dispatch(call_data['CALL'], call_data['ARGS'])
        print("\n[ORION]:\n", result)
    else:
        print("\n[ORION]: No se pudo interpretar la instrucción.")
