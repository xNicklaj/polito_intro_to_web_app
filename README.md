# Aronica Simone s280822
## Requisiti
L'unico requisito a livello di sistema è che python sia configurato in modo tale da poter avviare moduli python direttamente da terminale, in quanto è necessario far uso dell'applicativo di flask per avviare il server. 

E.g. `flask run`

Le dependencies python si trovano come per standard in requirements.txt.

## Startup
Una volta configurato python come da requisiti, è possibile avviare il server in tre modi.
### Avvio automatico tramite bat/sh
Ho creato uno script di avvio automatico sia per linux che per windows (`start.[sh|bat]`) che si occupa automaticamente di setup e avvio.
### Avvio automatico tramite task di VS Code
Il package.json del progetto include dei task di avvio che richiamano automaticamente gli script di avvio per linux o windows, quindi è possibile avviare il server anche tramite task di vscode.
### Avvio manuale
Per avviare manualmente è necessario configurare una variabile di sistema:
```
{
    'FLASK_APP'=app\init.py
}
```
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