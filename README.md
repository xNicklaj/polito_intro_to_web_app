# Aronica Simone s280822
## Requisiti
L'unico requisito a livello di sistema è che python sia configurato in modo tale da poter avviare moduli python direttamente da terminale, in quanto è necessario far uso dell'applicativo di flask per avviare il server. 

E.g. `flask run`

Le dependencies python si trovano come per standard in requirements.txt.

Prima di avviare il server è necessario eseguire `setup.py` per scaricare dei requirements di `rake-nltk`. 
Il download stamperà a schermo il percorso in cui verranno estratti i file, quindi tienilo a portata di mano per la futura rimozione dei file. Questa operazione verrà effettuata automaticamente tramite gli script di avvio automatico.

## Startup
Una volta configurato python come da requisiti, è possibile avviare il server in due modi.
### Avvio automatico tramite ps1/sh
Ho creato script di avvio automatico sia per linux che per windows (`start.[sh|ps1]`) che si occupa automaticamente di setup e avvio.

Passo fondamentale: prima di avviare lo script, sei sei su windows, apri il terminale da cui avvierai l'istanza del server e usa il comando:
```
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```
### Avvio manuale

Per avviare manualmente è necessario configurare una variabile di sistema:
```
FLASK_APP=app\__init__.py
```
Inoltre è necessario eseguire `setup.py`.

Dopo ciò, si può avviare eseguendo il comando `flask run --host=0.0.0.0`

Nota: è sufficiente impostare la variabile di sistema per la sessione corrente di terminale, inoltre, non è necessario specificare `--host=0.0.0.0`, ma permette di provare il sito nativamente da mobile.
### Credenziali utenti
Il database include già alcuni utenti di prova, le cui credenziali sono qui descritte:

| Nome utente       | Password | IsCreator |
| ----------------- | -------- | --------- |
| vAbEgran          | 2EWZcf2h | True      |
| AostaValley       | ep6CJxpJ | True      |
| SaifulAimran      | rww4Lq9F | True      |
| Anastaia_of_crete | npVCD3RE | True      |
| maineger          | bZpukrPt | False     |
| GabriTheBeer      | Yxs8Rpwj | False     |
| Phr0nemos         | RhMGE9w3 | False     |