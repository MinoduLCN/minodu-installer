from pyinfra.operations import server, python, files
from pyinfra import config

config.SUDO = True

server.shell(
    name="Pull latest changes of minodu repo",
    commands=["su - pi -c 'cd /home/pi/minodu && git pull --ff-only'"]
)

files.file(
    name="Remove downloaded database file",
    path="/home/pi/minodu/tools/sync/download.zip",
    present=False,
)

server.shell(
    name="Sync local database with server",
    commands=[
        "su - pi -c 'cd /home/pi/minodu && npm run sync:database'",
    ]
)

server.shell(
    name="Update RAG embeddings (runs in background, takes a few hours)",
    commands=[
        "systemd-run --uid=pi --gid=pi "
        "--working-directory=/home/pi/minodu "
        "--unit=rag-sync --collect "
        "bash -lc 'npm run sync:rag'",
    ],
)

def print_summary(state, host):
        print("""
        =============================================
        Update finished successfully!
              
       The vector database is now beeing rebuild.
        Dont turn of your pi for a few hours. 
        You can check its success on the pi by logging in via ssh 
        and running `systemctl status rag-sync` to see its status.
        The service will dissapear once it build the whole database.
        Run `cd /home/pi/minodu && npm run info:rag` to print out the
        content of the rags vector database.
              
        You can rerun the building of the rag database by running:
        pyinfra @ssh/minodupi.local 09_build_rag_db.py -v --ssh-user="pi" --ssh-password="<your-password>"
        
        =================
        ============================
        """)
    
python.call(
    name="Print final update summary",
    function=print_summary,
)