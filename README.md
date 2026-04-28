# Advanced Heat Transfer Optimization con Modelli TPMS

Questo programma Python svolge l'ottimizzazione e il calcolo delle prestazioni per uno scambiatore di calore basato sulle architetture avanzate TPMS. 
Il suo scopo principale è **estrapolare il numero minimo di celle unitarie necessarie per raggiungere una determinata efficienza di scambio termico.**

## Breve introduzione ai TPMS

Le superfici **TPMS** (Triply Periodic Minimal Surfaces) si ripiegano tridimensionalmente nello spazio proponendo sempre curvatura media nulla, sviluppandosi fluidamente nello spazio 3D senza intersezioni brusche o bordi. 

Grazie alla vasta e simmetrica area superficiale in un minuscolo spazio-volume (topologie ad esempio *Diamond, Gyroid, Lidinoid, o Primitive/Schoen*), garantiscono caratteristiche termofluidodinamiche imparagonabili a classiche strutture cellulari e ai convenzionali scambiatori termici. Ottimizzano l'alta efficienza energetica accoppiata ad un mescolamento dei fluidi che promuove minimi dislivelli di cadute di pressione. 

---

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the scripts in the `assignment1/` folder to perform the analyses. For example:
```bash
python assignment1/project1.py
```

### Git Workflow
To manage your project with Git, follow these steps:
- **Synchronize files**: Ensure your local repository is up-to-date by pulling the latest changes.
- **Modify files**: Make the necessary changes to your files.
- **Save changes**: Save the modified files (Control + S).
- **Stage changes**: Use the `+` icon next to the modified files under the "Changes" section to stage them.
- **Commit changes**: From the commit dropdown, enter a descriptive commit message indicating what was modified.
- **Push changes**: Save the commit and push it to the remote repository.

## License
This project is for educational purposes only.
