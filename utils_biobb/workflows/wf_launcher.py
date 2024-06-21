import argparse
import requests
import subprocess
import os
import socket
import webbrowser
from pathlib import Path


# Function to get options from the API
def get_options_from_api(api_url):
    response = requests.get(api_url)
    data = response.json()
    return data


# Function to ask the user to choose an option from a list of options given by the API
def ask_user_to_choose_option(options):
    choice = -1
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option['title']}")
    while choice < 0 or choice >= len(options):
        try:
            choice = int(input("✅ Choose an option by number: ")) - 1
            if choice < 0 or choice >= len(options):
                print(f"Invalid choice. Please choose a number within the correct range [1 - {len(options)}].")
        except ValueError:
            print("Invalid input. Please enter a number.")
    return options[choice]


# Function to check if Docker is running
def is_docker_running():
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.check_output(["docker", "info"], stderr=devnull)
        return True
    except subprocess.CalledProcessError:
        return False


# Function to check if connected to the internet
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


# Function to ask a question to the user with a list of choices
def ask_question(question, choices):
    response = ""
    while response not in choices:
        response = input(f"{question} ({'/'.join(choices)}): ").strip().lower()
        if response not in choices:
            print(f"Invalid choice. Please choose one of the following: {', '.join(choices)}")
    return response


# Function to check if a Docker image exists locally
def check_docker_image(image_name):
    try:
        image_id = subprocess.check_output(['docker', 'images', '-q', image_name])
        return image_id.decode('utf-8').strip() != ''
    except subprocess.CalledProcessError:
        return False


# Function to check if a Docker container is running in a specific port
def check_docker_port(port):
    try:
        container_id = subprocess.check_output(['docker', 'ps', '-qf', f'publish={port}'])
        return container_id.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None


def main():
    try:

        parser = parser = argparse.ArgumentParser(description='''╔════════════════════════════════════════════════════════════════════════════════════╗\n║                                                                                    ║\n║  🐳 Run a Docker container BioBB workflow 🧱 via Jupyter Notebook 📋 or Python 🐍  ║\n║                                                                                    ║\n╚════════════════════════════════════════════════════════════════════════════════════╝\nSelect one of the BioBB workflows and run it via docker!''', formatter_class=argparse.RawTextHelpFormatter)
        # parser.add_argument('-i', '--input', type=str, help='Input file')
        parser.parse_args()

        # Check if connected to the internet
        if not is_connected():
            print("🚫 Not connected to the internet. Please check your connection and try again.")
            exit(1)

        # Check if Docker is running
        if is_docker_running():
            print("🐳 Docker is running")
        else:
            print("🚫 Docker is not running. Please start Docker and try again.")
            exit(1)

        api_url = "https://mmb.irbbarcelona.org/biobb/api/v1/info/wf/"
        options = get_options_from_api(api_url)
        chosen_wf = ask_user_to_choose_option(options)
        wf_id = chosen_wf["id"] + "_" + chosen_wf["subid"] if chosen_wf.get("subid") else chosen_wf["id"]

        # ask for working dir
        wd = input("📂 Define absolute path for working dir (leave blank for using current folder): ")
        if wd == "":
            wd = Path.cwd()
        else:
            if not Path(wd).exists():
                print(f"🚫 Working dir {wd} does not exist. Exiting...")
                exit(1)

        # ask mode (jupyter or python)
        type = ask_question("❓ Would you like to execute the WF in Jupyter Notebook 📋 or Python 🐍 mode?", ["j", "p"])

        # ask for custom workflow file
        custom = ask_question("🔁 Do you want to override the workflow file?", ["y", "n"])

        ft = {"p": ".py", "j": ".ipynb"}
        custom_file = ""
        # if custom, ask for custom file absolute path
        if custom == "y":
            custom_file = input(f"Enter the file name for the custom workflow {ft[type]} file (it must be in the {wd} folder): ")
            custom_file_path = Path(wd) / custom_file
            if not custom_file_path.exists():
                print(f"🚫 Custom workflow file {custom_file_path} does not exist. Exiting...")
                exit(1)
            if not custom_file.endswith(ft[type]):
                print(f"🚫 Custom workflow file {custom_file} does not have the {ft[type]} extension. Exiting...")
                exit(1)

        # check if docker image exists locally
        docker_img = f"biobb/{wf_id}"
        if check_docker_image(docker_img):
            print(f"🎉 Docker image {docker_img} exists locally.")
        else:
            # pull docker image
            print(f"⏬  Docker image does not exist locally, pulling Docker image {docker_img}...")
            try:
                subprocess.check_call(['docker', 'pull', docker_img])
                print(f"🎉 Successfully pulled Docker image {docker_img}.")
            except subprocess.CalledProcessError:
                print(f"🚫 Failed to pull Docker image {docker_img}.")
                exit(1)

        #  docker run
        if type == "j":
            print(f"🚀 Running workflow {chosen_wf['title']} in Jupyter Notebook 📋 mode...")
            # ask for the port
            port = input("⚙️  Define the port for the Jupyter Notebook (leave blank for using default 3000): ")
            # define default port
            if port == "":
                port = "3000"
            # check if port is already in use
            container_id = check_docker_port(port)
            # if port is in use, stop the container
            if container_id:
                print(f"🛑 Stopping running container with image {docker_img} on port {port}...")
                subprocess.check_call(['docker', 'stop', f'{container_id}'])
            # run the container in jupyter mode
            print(f"📂 All the data generated by the workflow will be stored in the new {Path(wd) / 'wf_notebook'} folder")
            subprocess.check_call(['docker', 'run', '-d', '-e', f'REPO={wf_id}', '-e', 'MODE=jupyter', '-e', f'USER_JN={custom_file}', '-p', f'{port}:8888', '-v', f'{wd}:/data', docker_img])
            print(f"🔗 Opening Jupyter Notebook in the browser, it can take a few seconds... If browser doesn't open, please try it manually by typing http://localhost:{port}/notebooks/notebook.ipynb")
            # open the browser
            webbrowser.open(f"http://localhost:{port}/notebooks/notebook.ipynb")
        else:
            # run the container in python mode
            print(f"🚀 Running workflow {chosen_wf['title']} in Python 🐍 mode...")
            print(f"📂 All the data generated by the workflow will be stored in the new {Path(wd) / 'wf_python'} folder")
            subprocess.check_call(['docker', 'run', '-e', f'REPO={wf_id}', '-e', 'MODE=python', '-e', f'USER_PY={custom_file}', '-v', f'{wd}:/data', docker_img])
            print(f"📂 All the data generated by the workflow will be stored in the new {Path(wd) / 'wf_python'} folder")

    except KeyboardInterrupt:
        print("\n🚫 Program interrupted by user. Exiting...")
        exit(0)


if __name__ == "__main__":
    main()
