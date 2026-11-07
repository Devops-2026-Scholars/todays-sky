# Today's Sky Lab

A print copy of this guide is in `docs/Weather-Lab-Guide.pdf`.
You can send that file to your students.

This lab runs a small weather site on your Mac.
You will start three small programs and one web page.
Then you will open Argo CD and look at them.

Plan on about 90 minutes.
Some steps download big files.
Waiting is part of the lab.
A slow step can take 5 to 10 minutes.
Do not press Control+C while a step is working.
Control+C means stop.

Your teacher already put the programs in the folder.
You do not write the programs.
You start them, open them, and add one city.

## 1. What you are building

You will make a practice weather page.
It is for class.
It is not a live weather report.

Three programs do the work.
A program that does one job is called a microservice.

- locations is the City Book. It knows city names and map spots.
- forecast is the Sky Report. It makes the practice sky.
- gateway is the Front Desk. The web page talks only to this one.
- frontend is the web page. This is the one screen you see.

The programs talk like this:

```text
You
 |
 v
Web page
 |
 v
Front Desk
 |        \
 v         v
City Book  Sky Report
```

A tool named Argo CD shows the programs on a web page.
Argo CD also starts them from a notebook called Git.
When the notebook changes, Argo CD can change what is running.

## 2. Words you will use

Read these once.
The rest of the guide uses these words.

- Docker is the tool that builds a box around a program. You already have it.
- Docker Desktop is the Docker app on your Mac. It can also run Kubernetes.
- An image is the box, saved and ready.
- A container is a box that is running.
- Kubernetes is the leader that runs the boxes. If a box stops, Kubernetes can start it again.
- A cluster is the Kubernetes team on your Mac. You turn it on inside Docker Desktop.
- A pod is one running box inside the cluster.
- kubectl is the command that talks to the cluster.
- A context is the name of the cluster kubectl will use. Ours is `docker-desktop`.
- On the Kubernetes settings screen, the word kind is Docker's built-in starter. You do not install it. You do not type it.
- Git is a notebook that remembers every save.
- A push sends that notebook to GitHub.
- Argo CD is a web page. It reads the notebook and starts the programs. It shows you if they are healthy.

## 3. Before you start

Check this list.

- [ ] You have an Intel MacBook Pro.
- [ ] Docker Desktop is already installed.
- [ ] Your teacher gave you the lab folder. Its name is `Kubernet mat`.
- [ ] The Mac can use the internet. The first steps download big files.
- [ ] You have about 90 minutes.
- [ ] Docker may use at least 6 GB of memory.
- [ ] The Mac has at least 10 GB of free disk space.

You will turn Kubernetes on inside Docker Desktop.
That is the cluster for this lab.
Give it time. The first start can take several minutes.

## 4. Open Terminal

Terminal is where you type commands.

1. Press the Command key and the Space bar at the same time.
2. Type `Terminal`.
3. Press Return.

A window opens.
You type a command, then press Return to run it.

Copy a whole gray box.
Click the Terminal window.
Press Command+V to paste.
If the last line is still sitting there, press Return.

You are ready for the next command when you can type again.
On many Macs the line ends with `%`.

When the guide says to use a second window:

1. Click the Shell menu at the top of the screen.
2. Click New Window.

Leave the first window open.

## 5. Go to the lab folder

Every later command that uses a file must run from the lab folder.

1. Type `cd` and one space. Do not press Return yet.
2. Open Finder and find the folder named `Kubernet mat`.
3. Drag that folder into the Terminal window.
4. Press Return.

```bash
pwd
ls
```

> You should see: a path that ends with `Kubernet mat`.
> You should see: README.md, argocd, deploy, frontend, lab, and services.

If those names are missing, you are in the wrong folder.
Drag the folder in again.

Stay in this folder.
If you open a new Terminal window for a file command, drag the folder in again.
`kubectl` commands can run from any folder after the cluster is running.
Using the lab folder every time is the simple way.

## 6. Check your Mac

```bash
uname -m
docker version
docker info --format '{{.MemTotal}}'
df -h /
```

> You should see: `x86_64`. That means Intel. This guide is for that chip.
> You should see: a Client block and a Server block in the Docker output.
> You should see: a memory number. `6000000000` means about 6 GB. Your number should be at least that big.
> You should see: the word Avail, with 10Gi or more.

If `uname -m` prints `arm64`, this is not an Intel Mac.
Stop and tell your teacher.

If `docker version` has no Server block, Docker is not running.
Open Docker Desktop.
Wait until the whale icon is steady.
Run `docker version` again.

If the memory number is smaller than `6000000000`:

1. Click the whale icon.
2. Click Settings.
3. Click Resources.
4. Move Memory to 6 GB or more.
5. Click Apply & restart.
6. Wait until Docker is ready.
7. Run the memory command again.

If Avail is under 10Gi, delete files you do not need.
Then run `df -h /` again.

## 7. Check kubectl

kubectl talks to the cluster.
Docker Desktop often installs it for you.

```bash
kubectl version --client
```

> You should see: `Client Version: v1.36.1`.

That version matches the cluster on the Docker screen.
If you see `v1.36.1`, go to the next step.
Do not install kubectl again.

If you see `command not found`, install the matching version:

```bash
mkdir -p "$HOME/bin"
KURL="https://dl.k8s.io/release/v1.36.1/bin/darwin/amd64/kubectl"
curl -fsSL -o "$HOME/bin/kubectl" "$KURL"
chmod +x "$HOME/bin/kubectl"
echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
export PATH="$HOME/bin:$PATH"
kubectl version --client
```

> You should see: `Client Version: v1.36.1`.

## 8. Turn on Kubernetes

Open Docker Desktop.
Click the whale icon at the top of the screen.
Click Settings.
Click Kubernetes.

A correct screen looks like this.

- Enable Kubernetes is on. The switch is blue.
- The cluster name is `docker-desktop`.
- The status says Running. The dot is green.
- Under the name you see `kind, 1 node, v1.36.1`.
- Choose cluster provisioning method says `kind`.
- Kubernetes version says `1.36.1`.
- Nodes is `1`.

This screen is correct.
Leave it like that.

The word kind on this screen is Docker's built-in way to start the cluster.
You do not install Kind.
You do not type `kind` in Terminal.

Leave the version at `1.36.1`.
Leave nodes at `1`.
Do not click the red Reset cluster button.
That button deletes the cluster.

If Enable Kubernetes is already on and the status says Running, go to the next step.
Do not change the dropdowns.

If the switch is off, turn the cluster on:

1. Click Enable Kubernetes so the switch is on.
2. Set the provisioning method to `kind`.
3. Set the Kubernetes version to `1.36.1`.
4. Set nodes to `1`.
5. Click Apply & restart.
6. Wait until the status says Running and the dot is green.

The first start can take several minutes.
Leave the laptop open.
Do not click Reset cluster while you wait.

## 9. Point kubectl at Docker Desktop

A context tells kubectl which cluster to use.
This lab uses the context named `docker-desktop`.

```bash
kubectl config use-context docker-desktop
kubectl get nodes
```

> You should see: `Switched to context "docker-desktop"`.
> You should see: one node. STATUS says Ready. VERSION says `v1.36.1`.
> The node name can be `desktop-control-plane`. That name is correct.

If the STATUS says NotReady, wait one minute.
Run `kubectl get nodes` again.
When it says Ready, go on.

## 10. Install Argo CD

This step downloads big files.
Wait until the pods are ready.
That often takes 3 to 5 minutes.

```bash
kubectl create namespace argocd
TAG="v3.6.1"
HOST="https://raw.githubusercontent.com"
URL="$HOST/argoproj/argo-cd/$TAG/manifests/install.yaml"
kubectl apply -n argocd -f "$URL"
kubectl -n argocd get pods
```

> You should see: the word `created` or `configured` many times.
> You should see: about 7 pods.

Run the last command again after one minute.
Keep going until every line says Running and the READY column says `1/1`.

```bash
kubectl -n argocd get pods
```

> You should see: every pod Running, and every READY value `1/1`.

If a line says ContainerCreating or PodInitializing, wait.
Leave Kubernetes turned on.
Look at the fix page only if a pod still says ImagePullBackOff or Error after 10 minutes.

## 11. Open the Argo CD page

Argo CD can speak a simple web language.
This patch turns that on.
Then you restart the Argo CD page so the change is used.

```bash
CM=argocd-cmd-params-cm
PATCH='{"data":{"server.insecure":"true"}}'
kubectl -n argocd patch configmap "$CM" --type merge -p "$PATCH"
kubectl -n argocd rollout restart deployment argocd-server
kubectl -n argocd rollout status deploy/argocd-server --timeout=300s
```

> You should see: `configmap/argocd-cmd-params-cm patched`.
> You should see: `successfully rolled out`.

Now open a second Terminal window.
In that second window, paste this command.
It will not finish.
That is correct.
Leave that window open the whole time you use Argo CD.

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80
```

> You should see: `Forwarding from 127.0.0.1:8080 -> 8080`.

Open your web browser.
Go to this address:

```text
http://localhost:8080
```

Use `http://`.
The address does not use `https://`.

## 12. Sign in

In the first Terminal window, print the password.

```bash
NAME=argocd-initial-admin-secret
OUT=/tmp/pw.b64
Q='{.data.password}'
kubectl -n argocd get secret "$NAME" -o jsonpath="$Q" > "$OUT"
base64 -D -i "$OUT"
echo
rm "$OUT"
```

> You should see: one long line of letters and numbers.

That line is the password.
It has no spaces.
Copy the whole line.

On the Argo CD page:

1. The username is `admin`. Type it in small letters.
2. Paste the password.
3. Click Sign In.

> You should see: the Argo CD applications page.
> You may see an empty list. That is fine. The weather app is not added yet.

If the page will not open, look at the second window.
The Forwarding line must still be there.
If that window stopped, paste the port-forward command again.

## 13. Build the programs

Go back to the first Terminal window.
You must be in the lab folder.
These commands build five images on your Mac.
Four are the weather parts.
One is the Git notebook server.
The notebook server is a helper.
It is not one of the three microservices.

Each build can take a few minutes the first time.
Wait until you can type again before you worry.
You should not see the word ERROR.

```bash
TAG=weather-locations:1.0.0
docker build --platform linux/amd64 -t "$TAG" services/locations
TAG=weather-forecast:1.0.0
docker build --platform linux/amd64 -t "$TAG" services/forecast
TAG=weather-gateway:1.0.0
docker build --platform linux/amd64 -t "$TAG" services/gateway
TAG=weather-frontend:1.0.0
docker build --platform linux/amd64 -t "$TAG" frontend
TAG=weather-git-server:1.0.0
docker build --platform linux/amd64 -t "$TAG" lab/git-server
```

> You should see: each build finishes, and you can type again.

`--platform linux/amd64` means the box matches an Intel Mac.

Do not send these images to the internet.
Do not run `docker push`.
Docker Desktop lets Kubernetes use the images you just built.
The setup files already say to use the local image when it is here.
Build them, then go to the next step.

## 14. Start the Git notebook

This step is optional.
This class keeps the notebook on GitHub.
Argo CD reads that GitHub notebook.
The lines below start a Git notebook inside the cluster.
Use them only if your teacher says to.
Your Mac would open that notebook at door 30090.

```bash
kubectl apply -f lab/git-server.yaml
kubectl -n git rollout status deploy/git-server --timeout=180s
kubectl -n git get pods
```

> You should see: `deployment "git-server" successfully rolled out`.
> You should see: the git-server pod Running, and READY `1/1`.

## 15. Save your work in Git

These name lines last for this window only.
They do not change the Git settings on the Mac.
The push sends the notebook to GitHub.
Argo CD will read it from there.

```bash
git init -b main
export GIT_AUTHOR_NAME="Student"
export GIT_AUTHOR_EMAIL="student@example.com"
export GIT_COMMITTER_NAME="Student"
export GIT_COMMITTER_EMAIL="student@example.com"
git add .
git commit -m "Add the weather lab"
ORIGIN=https://github.com/Devops-2026-Scholars/todays-sky.git
git remote add origin "$ORIGIN"
git push -u origin main
```

> You should see: a list of file names in the commit.
> You should see: a push line with `main`.

If the commit says `nothing to commit`, that is fine.
If Git says `remote origin already exists`, skip the add line.
Then run the push line.

If the push asks you to sign in, use your GitHub account.
Do not type your Mac password into Git.
If you cannot sign in, tell your teacher.

## 16. Ask Argo CD to run the app

This file tells Argo CD where the notebook is.
Argo CD reads the `deploy` folder and starts the weather parts.

```bash
kubectl apply -f argocd/application.yaml
kubectl -n weather get pods
```

Wait about one minute.
Run the pod command again.

> You should see: four pods. The names start with locations, forecast, gateway, and frontend.
> You should see: each one Running, and READY `1/1`.

Then look at the Argo CD page in the browser.
Click Refresh if you see that button.

> You should see: an application named `weather`.

Click the weather row.

> You should see: the word Synced.
> You should see: the word Healthy.
> You should see: locations, forecast, gateway, and frontend.

Green means healthy.
Synced means the cluster matches the Git notebook.

## 17. Open the weather page

Keep the Argo CD window running.
Open a new browser tab.
Go to:

```text
http://localhost:30080
```

> You should see: the title Today's Sky.
> You should see: buttons for Lagos, London, New York, Tokyo, Nairobi, and Paris.

Click Lagos.
Then click London.

> You should see: a big Celsius number, a sky word, and a short sentence.
> You should see: Lagos with a higher number than London.

The number is a practice sky.
It uses the map spot and today's date.
It does not call a real weather company.
The same city keeps the same number all day.
That is how you know the lab is steady.

## 18. Look around Argo CD

Go back to the Argo CD tab.
Open the weather application if you are not already inside it.

Find the four names.

- locations is the City Book.
- forecast is the Sky Report.
- gateway is the Front Desk.
- frontend is the web page.

Click one pod name if the page lets you.
You can look around.
Do not delete anything.

Argo CD is the window.
Kubernetes is the leader that keeps the pods running.
Git is the notebook Argo CD trusts.

## 19. Add the city Accra

You will change the city list.
You will save it in Git.
Argo CD will update the running City Book.

Open the file `deploy/cities.json` in a plain text editor.
Cursor is a good editor.
TextEdit is fine only if you first click Format, then Make Plain Text.
Do not use Pages or Word.
Those tools add hidden marks and break the file.

Find the Paris block at the end.
Put a comma after the Paris `}`.
Then add Accra.
The end of the file should look like this:

```json
  {
    "id": "paris",
    "name": "Paris",
    "country": "France",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  {
    "id": "accra",
    "name": "Accra",
    "country": "Ghana",
    "latitude": 5.6037,
    "longitude": -0.1870
  }
]
```

The Paris block now has a comma after it.
The Accra block does not have a comma after it.
Save the file.

In the first Terminal window, run:

```bash
git add deploy/cities.json
git commit -m "Add Accra to the city list"
git push origin main
```

> You should see: a commit line.
> You should see: the push mention `main`.

Go to the weather app in Argo CD.
Click Refresh.
If you see a button named Sync, click it, then click Synchronize.

Wait until locations is green again.
This can take one minute.
Argo CD starts a new City Book pod so it reads the new file.

Reload the weather page.
Use http://localhost:30080

> You should see: an Accra button.
> Click Accra. You should see a practice sky for Accra.

## 20. If something goes wrong

Change one thing.
Then try the step again.
Leave Kubernetes turned on while you fix a step.

### Docker will not answer

Open Docker Desktop.
Wait for the whale icon to be steady.

```bash
docker version
```

> You should see: a Server block.

### The chip check is not x86_64

This guide is for Intel Macs.
`x86_64` is the Intel answer.
Stop and tell your teacher if you see a different word.

### Kubernetes is still starting

```bash
kubectl config use-context docker-desktop
kubectl get nodes
```

If you see `connection refused`, Kubernetes is still starting.
Wait two minutes.
Open Settings, then Kubernetes.
The status must say Running, and the dot must be green.
Then run `kubectl get nodes` again.

> You should see: one node, STATUS Ready, VERSION `v1.36.1`.

If it still says connection refused after 10 minutes, tell your teacher.
Do not click Reset cluster.
Do not turn the switch off and on again while it is starting.

### The settings screen says kind

That word is correct.
It is Docker's built-in way to start the cluster.
You do not install Kind.
You do not type `kind` in Terminal.
Leave the version at `1.36.1` and nodes at `1`.

### kubectl talks to the wrong place

```bash
kubectl config use-context docker-desktop
kubectl config current-context
kubectl get nodes
```

> You should see: `docker-desktop`.
> You should see: one Ready node.

### kubectl says command not found

Close Terminal and open it again.
If you installed kubectl in this lab, run this first:

```bash
export PATH="$HOME/bin:$PATH"
kubectl version --client
```

If it still says command not found, repeat the install lines in "Check kubectl".

### A door is already in use

```bash
lsof -nP -iTCP:30080 -sTCP:LISTEN
lsof -nP -iTCP:30090 -sTCP:LISTEN
lsof -nP -iTCP:8080 -sTCP:LISTEN
```

If a line is printed, that door is busy.
Ask your teacher before you stop the other program.

For Argo CD only, you can use door 8088:

```bash
kubectl port-forward svc/argocd-server -n argocd 8088:80
```

Then open http://localhost:8088

The weather page stays on http://localhost:30080.
The optional Git notebook stays on http://127.0.0.1:30090.

### Argo CD pods stay unready

Wait the full 10 minutes on a slow network.
Then run:

```bash
kubectl -n argocd get pods
kubectl -n argocd describe pod -l app.kubernetes.io/name=argocd-server
```

If the text says ImagePullBackOff, the Mac could not download Argo CD.
Check the internet.
Then delete that pod so Kubernetes tries again:

```bash
kubectl -n argocd delete pod -l app.kubernetes.io/name=argocd-server
```

### The Argo CD page will not load

The second Terminal window must still show Forwarding.
If it stopped, paste the port-forward command again.

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80
```

The address is http://localhost:8080
Use http, not https.

If the browser shows a certificate warning, the simple web setting was missed.
Run the patch and restart lines from "Open the Argo CD page" again.
Then start the port-forward again.

### Sign in fails

The user name is `admin`.
Run the password lines again.
Copy the new line.
The password has no spaces.

### A weather pod says ImagePullBackOff

Kubernetes could not find the image on this Mac.
The name and the tag must match the build.
Run:

```bash
docker images
```

> You should see: weather-locations, weather-forecast, weather-gateway, weather-frontend, and weather-git-server.
> Each tag should be `1.0.0`.

If a name is missing, run its build lines again from "Build the programs".
Do not push the image to the internet.
Then start the pods again:

```bash
kubectl -n weather delete pod -l app.kubernetes.io/part-of=weather
kubectl -n git delete pod -l app.kubernetes.io/name=git-server
kubectl -n weather get pods
kubectl -n git get pods
```

> You should see: Running and `1/1`.

### Git push does not work

The class notebook is on GitHub.
The push line is `git push origin main`.

If Git says `Authentication failed`, you are not signed in
to the class GitHub account.
Tell your teacher.
Do not type your Mac password.

The notes below are only for the optional Git notebook
inside the cluster.

```bash
kubectl -n git get pods
kubectl -n git logs deploy/git-server --tail=30
```

> You should see: the git-server pod Running.

If the pod is missing, run the lines in "Start the Git notebook" again.
Then run the push line again.

If the git pod just restarted, the notebook may be empty.
Run the push line again.

If Git says `terminal prompts disabled`, the notebook server did not accept the push.
Read the log lines to your teacher.

If Git says `nothing to commit` and the push says `up-to-date`, the file was not saved.
Save `deploy/cities.json` and run the add, commit, and push lines again.

### The weather page does not open

```bash
kubectl -n weather get pods
```

All four pods must be Running and `1/1`.
The address is http://localhost:30080

### The page says the city list file is not valid

A comma or a quote is wrong.
You can replace the whole file with the city list in the next section.
Save it.
Then run:

```bash
git add deploy/cities.json
git commit -m "Fix the city list"
git push origin main
```

Click Refresh in Argo CD.
Wait until locations is green.
Reload the weather page.

### A good cities.json file

This copy includes Accra.
If you have not added Accra yet, you can stop at Paris and leave no comma after Paris.

```json
[
  {
    "id": "lagos",
    "name": "Lagos",
    "country": "Nigeria",
    "latitude": 6.5244,
    "longitude": 3.3792
  },
  {
    "id": "london",
    "name": "London",
    "country": "United Kingdom",
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  {
    "id": "new-york",
    "name": "New York",
    "country": "United States",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  {
    "id": "tokyo",
    "name": "Tokyo",
    "country": "Japan",
    "latitude": 35.6762,
    "longitude": 139.6503
  },
  {
    "id": "nairobi",
    "name": "Nairobi",
    "country": "Kenya",
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  {
    "id": "paris",
    "name": "Paris",
    "country": "France",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  {
    "id": "accra",
    "name": "Accra",
    "country": "Ghana",
    "latitude": 5.6037,
    "longitude": -0.1870
  }
]
```

### Accra does not show up

1. Save the file.
2. Make sure the commit command printed a new commit.
3. Make sure the push printed `main`.
4. Click Refresh on the weather app in Argo CD.
5. Wait until the locations pod is green.
6. Reload http://localhost:30080

### A pod says CrashLoopBackOff

Read the last lines.
They often name the problem.

```bash
kubectl -n weather logs deploy/locations --tail=40
kubectl -n weather logs deploy/forecast --tail=40
kubectl -n weather logs deploy/gateway --tail=40
kubectl -n weather logs deploy/frontend --tail=40
```

### You pressed Control+C in the Argo CD window

That stops the page, not the cluster.
Paste this again and leave it running:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80
```

## 21. Turn the lab off

Click the second Terminal window.
Press Control+C.
That closes the Argo CD page on your Mac.
The programs can keep running.

When you want the memory back, turn Kubernetes off:

1. Click the whale icon.
2. Click Settings.
3. Click Kubernetes.
4. Click Enable Kubernetes so the check goes away.
5. Click Apply & restart.
6. Wait until Docker is ready.

Your images can stay in Docker.
They do no harm.
The next time you turn Kubernetes on, build again only if `docker images` is missing a `1.0.0` tag.

## 22. How the pieces fit

The City Book, the Sky Report, and the Front Desk are the three microservices.
The web page is the one screen.
The Git notebook server is only a helper for the lab.

Each microservice lives in its own folder.

- `services/locations` is the City Book.
- `services/forecast` is the Sky Report.
- `services/gateway` is the Front Desk.
- `frontend` is the web page.
- `deploy` holds the setup files Argo CD reads.
- `lab` holds the Git helper.
- `argocd/application.yaml` points Argo CD at the GitHub notebook.

Inside the cluster, each program has its own pod.
Each program can use door 8000.
They do not bump into each other.
The web page uses door 8080 inside its pod.
You open it on the Mac at door 30080.
The class notebook is on GitHub.
The optional Git notebook uses door 30090 on the Mac.

The web page never calls the City Book by itself.
It calls `/api/...` on its own address.
The page server sends that call to the Front Desk.
That keeps the browser on one address.

The Sky Report is a practice sky.
Places near the middle of the map come out warmer.
Places far north or south come out cooler.
The sky word comes from the city name and the date, so it stays put all day.
A real company would buy a weather feed.
This class does not, so every student can see a steady result.

The setup files ask Kubernetes to run each pod as a normal user.
They set a memory limit.
They open a health door named `/health`.
Kubernetes uses that door to see if the pod is ready.
They also say to use the image already on this Mac.
That is why you build the images and do not push them.

The city list that students edit is `deploy/cities.json`.
Argo CD turns that file into data the City Book reads.
When the file changes, the City Book pod starts again and reads the new list.

## 23. Teacher checks

Students can skip this page.
Run the lab once before class, on the same network the students will use.
That fills Docker with the big images.

From the lab folder, after Kubernetes is running:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

> You should see: all tests passed.

The tests check the City Book, the practice sky, and the Front Desk.
Lagos must come out warmer than London on the sample day.

To read what a program just did:

```bash
kubectl -n weather logs deploy/gateway --tail=20
```

Tools for this lab:

- Docker Desktop Kubernetes. Cluster name `docker-desktop`. Version `1.36.1`. One node.
- The settings screen says `kind`. That is Docker's built-in starter. Students do not install Kind and do not type kind commands.
- kubectl client `v1.36.1` matches this cluster.
- Argo CD v3.6.1
- Intel Macs use darwin amd64. `uname -m` prints `x86_64`.
- Do not click Reset cluster. That deletes the cluster.

The weather page is http://localhost:30080.
The class notebook is the GitHub repo todays-sky.
The optional local notebook is http://127.0.0.1:30090.
Argo CD is http://localhost:8080 while the port-forward is running.

To rebuild the print guide after you edit this README:

```bash
python3 -m pip install fpdf2
python3 docs/build_guide_pdf.py
```

The new file is `docs/Weather-Lab-Guide.pdf`.
