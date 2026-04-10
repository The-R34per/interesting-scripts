============================================================
PAYLOAD GENERATOR
Instructions & Usage Guide
============================================================

1. OVERVIEW
-----------
The Payload Generator is a utility that
automates common tasks used during exploit development.

It provides two major capabilities:

1. Encoding strings (Base64, Hex, URL)
2. Generating safe payload templates for:
   - Reverse shell scaffolding
   - Buffer overflow scaffolding

This tool does NOT generate harmful payloads. It only
automates structure, encoding, and boilerplate.


2. DIRECTORY STRUCTURE
-----------------------

payload_generator/
    payload_generator.py
    templates/
        reverse_shell_template.txt
        bof_template.txt

The templates folder contains placeholder files that the
tool fills in when generating output.


3. HOW TO RUN THE TOOL
-----------------------

The tool has two modes:

A) Encoding Mode
B) Template Generation Mode

You select a mode using the first argument.


------------------------------------------------------------
A) ENCODING MODE
------------------------------------------------------------

Usage:

    python3 payload_generator.py encode <type> <data>

Supported encoding types:
- base64
- hex
- url

Examples:

    python3 payload_generator.py encode base64 "Hello"
    python3 payload_generator.py encode hex "Hello"
    python3 payload_generator.py encode url "Hello World!"

The tool prints the encoded output directly to the terminal.


------------------------------------------------------------
B) TEMPLATE GENERATION MODE
------------------------------------------------------------

Usage:

    python3 payload_generator.py template <name> [--host HOST] [--port PORT]

Supported template names:
- reverse_shell
- bof

Examples:

    python3 payload_generator.py template reverse_shell --host 10.0.0.5 --port 4444

    python3 payload_generator.py template bof


4. TEMPLATE DETAILS
--------------------

A) reverse_shell_template.txt
-----------------------------
This is a placeholder structure for a reverse-shell style
workflow. It does NOT contain harmful code. It simply
provides a scaffold with {{HOST}} and {{PORT}} placeholders.

The tool replaces these placeholders when generating output.


B) bof_template.txt
-------------------
This template provides a basic buffer overflow payload
structure:

- OFFSET placeholder
- RET_ADDR placeholder
- Basic payload layout

You fill in the actual values during exploit development.


5. INTERNAL WORKFLOW
---------------------

A) Encoding
-----------
The tool takes the input string and applies the selected
encoding:

- Base64 → base64.b64encode()
- Hex    → .encode().hex()
- URL    → urllib.parse.quote()

The encoded result is printed immediately.


B) Template Generation
----------------------
1. The tool loads the selected template file.
2. It replaces {{HOST}} and {{PORT}} if provided.
3. The final template is printed to the terminal.


6. TYPICAL WORKFLOW
-------------------------------

Step 1: Generate a buffer overflow scaffold:

    python3 payload_generator.py template bof > bof_payload.txt

Step 2: Fill in:
- Offset
- Return address
- Payload structure

Step 3: Encode any strings needed for the exploit:

    python3 payload_generator.py encode base64 "USER admin"

Step 4: Generate a reverse-shell scaffold if needed:

    python3 payload_generator.py template reverse_shell --host <target> --port <port>

Step 5: Integrate the generated scaffolds into your exploit.


7. TROUBLESHOOTING
-------------------

Problem: "Template not found"
Solution: Ensure your folder structure is:

    payload_generator.py
    templates/
        reverse_shell_template.txt
        bof_template.txt

Problem: Output looks unchanged
Solution: You must pass --host and --port for reverse_shell
          if you want placeholders replaced.

Problem: Encoding output looks wrong
Solution: Wrap your input string in quotes.


8. SUMMARY
-----------
The Payload Generator automates repetitive tasks during
exploit development by providing:

- Fast encoding utilities
- Clean payload scaffolding

It is designed for speed, clarity, and workflow efficiency.

============================================================
END OF DOCUMENT
============================================================
