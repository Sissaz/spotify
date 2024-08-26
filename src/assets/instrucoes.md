## ⚙️ | First Installations
Commands for setting up a development environment: adjusting policies in PowerShell, installing pyenv, opening VSCode, using Poetry for dependency management and Python versions with pyenv, and Git commands for version control. Commands for pip and venv are mentioned but not used with Poetry.
<br>

I ran the following commands using Python in Visual Studio Code.

https://www.python.org/

https://code.visualstudio.com/


### In PowerShell

After opening PowerShell, type the following:

• Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Changes the execution policy of PowerShell to allow the execution of scripts.

<br>
• Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; & "./install-pyenv-win.ps1"

Downloads and executes the pyenv installation script for Windows.
<br><br>

### In Bash

After downloading Git Bash, open it in the project's current directory and type the following:

• code .

To open Visual Studio Code in the project's folder
<br><br>

### In VSCode

After opening VSCode, open the Git Bash terminal and type the following:

• pyenv install 3.12.1

Installs Python version 3.12.1 using pyenv. This allows you to manage multiple Python versions on the same system.

<br>
• pyenv local 3.12.1

Sets Python 3.12.1 as the version for the current directory.

<br>
• curl -sSL https://install.python-poetry.org | python3 -

Installs Poetry using the official script.

<br>
Verify the Poetry installation.

• python3 -m poetry --version

<br>
If needed, install Poetry using pip.

• pip install poetry

<br>
• poetry --version

Displays the installed version of Poetry.

<br>
• poetry config virtualenvs.in-project true

Configures Poetry to create virtual environments within the project.

<br>
• poetry new dados_csv 

Create the project and name it as you like.

<br>
• poetry install

After creating the project folder, open Git Bash in VSCode from within this folder. Then, run the command above to install the project dependencies specified in the pyproject.toml file

<br>
• poetry init

Starts a new project with Poetry, creating the pyproject.toml file.

<br>
• poetry shell

Activates the project's virtual environment.

<br>
• pyenv local 3.12.1

Sets the local version of Python to 3.12.1 using pyenv.

<br>
• poetry env use 3.12.1

Sets the Python version for the Poetry virtual environment.

<br>
• pyenv global 3.12.1

Sets the global version of Python to 3.12.1 using pyenv.

<br>
• poetry install --no-root

Installs the project dependencies without installing the root package.
<br><br>

### Installing Python Libraries with Poetry

• poetry add flask requests pandas python-dotenv werkzeug

Installs the necessary libraries required by this code using Poetry.
<br><br>

### Installing Other Python Libraries with Poetry
<br>
• poetry add streamlit

Adds the Streamlit library as a project dependency.

<br>
• poetry add streamlit

Adds the Streamlit library as a project dependency.

<br>
• poetry add duckdb

Adds the duckdb library as a project dependency.

<br>
• poetry add gdown

Adds the gdown library as a project dependency.

<br>
• poetry add psycopg2-binary

Adds the psycopg2-binary library as a project dependency.

<br>
• poetry add python-dotenv

Adds the python-dotenv library as a project dependency.

<br>
• poetry add psycopg2

Adds the psycopg2 library as a project dependency.

<br>
• poetry add sqlalchemy

Adds the SQLAlchemy library as a project dependency.

<br>
• poetry add pandas

Adds the pandas library as a project dependency.

<br>
• poetry add chardet

Adds the chardet library as a project dependency.
<br><br>

### Git Commands
• git add . or git add filename

Adds all changes to the Git index.

<br>
• git commit -m "update"

Creates a commit with the message "update".

<br>
• git push origin master

Pushes commits to the remote repository on the master branch.

<br>