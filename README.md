# Plateful: live prices that update themselves

This folder is the whole Plateful website plus a small robot that refreshes the Aldi, Lidl and Morrisons prices automatically, including sales: weekly, about every 2 days, or every day (you choose in step 14).

**Two ways to get live prices.** (1) The **home price checker** (see "Home price checker" below): free, runs on your own computer, covers Tesco, Sainsbury's, Morrisons and Lidl. (2) The **Apify robot** (steps 8 to 14): runs on GitHub's computers so your computer can be off, covers Aldi, Lidl and Morrisons, and costs money per search. You can use either, or both.

The website lets people pick **several meals at once** ("My shop"), set how many each feeds, and see the cheapest single shop for the whole basket. They can also **add their own recipes** (typing the ingredients they need), keep them in their own browser, and share them with a link. The robot looks after live prices for the **184 original ingredients**. The site itself now lists **526 products** (see "The product list" below).

It works anywhere in the UK. The prices are each shop's normal national prices from its website, so they are mostly the same wherever you are. A "Shops near you" setting (on the recipe, My shop, Leftovers, Budget and Shopping list pages; on a recipe page it sits under the dish picture, beside the prices, and on My shop it sits to the right of the prices) lets people untick any shop they can't get to, so only the shops they can use are compared, and an optional postcode box accepts any UK postcode (see "Nearest shops" below). The ticked shops and loyalty cards are saved in the person's own browser; the postcode is not saved at all. Small convenience stores, Northern Ireland and some islands can have different prices or shops, and the site says so. Saved baskets from earlier versions are moved to the new `plateful-basket` storage key the first time the page opens, so nobody loses what they saved.

There is also a **Leftovers** tab. People list what is left in their fridge and cupboards (picked from the ingredient list or typed in), and the site shows which meals they can make now, which they could make with up to three extra items (with the price of just those extras), and some quick no-recipe ideas and food-safety tips. The leftovers list is saved in their own browser, like their own recipes. Opening the tab plays a short intro (about 3 seconds): different cooking items fall into a bowl and pile up, then the scene drops away to reveal the page. It has a Skip button (or press Esc), it is skipped automatically for people who have "reduce motion" switched on, and it does not replay when you come back from a recipe. The "Tap to add common ones" block has a Clear button that un-picks the common items you tapped (anything you typed that is not one of those chips stays; "Clear the list" lower down still clears everything).

Opening **My shop** plays a similar short intro (about 3 seconds): groceries (a lettuce, oranges, milk, bread and a bottle of juice) drop one by one into a shopping basket, then the scene drops away to reveal the page. It follows the same rules as the Leftovers one: it has a Skip button (or press Esc), it is skipped for people who have "reduce motion" switched on, and it does not replay when you come back to My shop from a recipe you opened from it. It runs on real time (not frame by frame), so it still ends after about 3 seconds on a slow computer.

**Nearest shops.** When someone types their postcode and presses Check, a "Nearest shops" box lists the nearest real store of each of the 8 shops, nearest first, with the store's name, address and roughly how far away it is. If a small shop (Tesco Express, Sainsbury's Local, Morrisons Daily and so on) is closer than the nearest full-size one, it is shown underneath with a warning that small shops stock less and often charge more than the prices on the site. Shops with no store within 25 miles are named. The store list is real: about 10,900 stores from the free Geolytix Retail Points list (June 2026), built into the page, so the lookup happens on the person's own device and works with no internet connection. Distances are straight lines from the middle of the person's postcode sector (for example "BS7 8"), not road distances from their front door, and the page says so. Northern Ireland distances are rougher (measured from the middle of the district, like "BT1"). Shops open and close, so the list slowly goes out of date: Geolytix publishes a new one every few months.

**Google Maps.** Each store has one link, "Open in Google Maps". It opens Google Maps in a new tab with a pin dropped on that exact store (the link carries the store's map position, not its name). From there the person presses Google's Directions button and chooses how they want to get there: driving, walking, public transport or cycling. The site does not pick a route or a starting point for them. An earlier version searched Google by the store's name and address instead, but Google sometimes answered with a list of several branches rather than the one meant (2 of 11 Lidl links did when tried), so the link now goes by position, which always lands on one place. The trade-off is that Google's side panel shows the pin's map coordinates rather than the store's name and opening hours; the store's name and address are on the Plateful page next to the link. There is also a link that opens Google Maps showing every supermarket near the person's district. No Google account or API key is needed, and nothing from Google is loaded inside the page itself.

**What is kept about the postcode.** Nothing. The postcode is never saved: it is held only while the page is open, so the box is empty again every time the site is opened or reloaded, and the person types it again if they want the nearest shops. While the page is open it carries from page to page, so they only type it once per visit. Only the first half plus one digit is used (for example "BS7 8", which covers a few thousand homes); the last two letters, which are what narrow a postcode down to a street, are thrown away the moment Check is pressed. Typing just the first half ("BS7") works too. It is never sent to the site's owner, to GitHub or to the price robot, and it is not put in recipe share links or the copied shopping list. Google is only contacted when the person clicks an "Open in Google Maps" link, and is then given the store's map position, not the person's postcode (the "all supermarkets near" link gives Google the district, like "BS7", and only when clicked). A "Forget" button clears it straight away without reloading. A postcode saved by an earlier version of the site is removed from the browser's storage automatically the next time the page opens. One thing that is not Plateful: a browser's own autofill may offer the person's postcode as a suggestion when they click the box.

Opening **Shopping list** plays a third intro of the same kind (about 3 seconds): a checklist titled "Shopping list" has three lines written out with a pen, one at a time at a calm pace (about a third of a second each), and each box is ticked. The fourth box is left empty for you to fill. Meanwhile a carrot, lettuce, orange, tomato, milk, bread and banana swoop in around the list, then the scene drops away to reveal the page. It has the same Skip button, Esc key, reduced-motion rule and real-time clock as the other two.

Each of these three opening animations (Leftovers, My shop, Shopping list) plays **once per visit**: the first time that section is opened. After that, switching between the sections goes straight to the page, so the animation never gets in the way. Skipping one counts as having seen it. A "visit" lasts until the browser tab is closed, so reloading the page does not bring them back, and opening the site again in a new tab does.

**How it fits together**

- `index.html` is the website. When it opens, it reads `prices.json` (the current prices). If that file can't be read, it falls back to the prices baked into the page, so it never breaks.
- On the days you choose (step 14), GitHub runs `pipeline/update_prices.py`. On Mondays it searches the ingredients due that week; on the extra days (if you chose every 2 days or daily) it searches only the 89 everyday ingredients, which is where offers come and go. That script asks Apify to search each shop's website for the ingredients that are due that week (see "How often each ingredient is refreshed" below), throws away anything that isn't the plain everyday product, keeps the cheapest match for each pack size, and saves the result into `prices.json`.
- GitHub Pages serves the website from the same place, so the new prices appear on the site by themselves.
- Anything the robot can't refresh stays as it was. One broken shop never wipes the others.

**What it costs (please read before you start)**

- GitHub: free.
- Apify: with all three shops and 184 ingredients, the **worst case is about $6 in an average week, so roughly $26 a month**. That is a little above the $19 a month Apify's Starter plan costs (as far as I know the Starter plan includes about $19 of usage credit, so check Apify's pricing page). Apify bills per result returned, so the real figure is usually lower than this worst case. After your first full run (step 12), open Apify's **Billing** or **Usage** page to see what it really cost and decide from there.
- Morrisons is the dear one: about $15 of that $26. Aldi is about $7 and Lidl about $4. Using only Aldi and Lidl is about $11 a month at worst. Step 13 shows how to drop a shop with one setting.
- The test run in step 10 costs **50 cents at most** (usually less).
- As far as I know, Apify's free plan includes $5 of credit, which should cover the test run and probably one full run (step 12), so you can see it working before you pay anything. Check your Apify Billing page to confirm.
- Nothing runs on a schedule, and nothing is billed weekly, until you do step 14. Until then you run it by hand.

**What you need to do yourself.** I can't create accounts, and I never see or handle your API token. That's why the steps below are yours: creating the GitHub account, making the repository, and pasting the Apify token into GitHub's secret box. Each step says what you should see afterwards and what to do if you don't.

---

## Setting it up

### Step 1. Make a GitHub account

1. Go to **github.com** and click **Sign up**. Follow the prompts (email, password, username, verification puzzle).
2. Your username becomes part of your website's address, for example `yourname.github.io/plateful`. Pick one you're happy to show people.

**You should see:** the GitHub home page with your username in the top right.

**If you already have an account,** just sign in and carry on.

### Step 2. Make the repository (the folder that holds everything)

1. Click the **+** in the top right, then **New repository**.
2. **Repository name:** `plateful`
3. Choose **Public**. (GitHub Pages is free for public repositories. It also means anyone can see the files, which only contain prices and the recipe site, nothing personal.)
4. **Leave "Add a README file" switched off.**
5. Click **Create repository**.

**You should see:** an almost empty page titled with your username and `plateful`, with a box of setup instructions and a link that says **uploading an existing file**.

**If you don't see that link:** click **Add file** (top right of the file list), then **Upload files**.

### Step 3. Upload the files

1. On your computer, unzip `plateful-auto.zip`. You get a folder called `plateful-auto`.
2. Open that folder. You should see `index.html`, `404.html`, `prices.json`, `robots.txt`, `favicon.svg`, `apple-touch-icon.png`, `og-image.png`, `README.md`, and folders called `pipeline`, `github-workflow` and `licences`.

**Already set this up with the earlier version?** Skip steps 1 to 9. Instead: on GitHub open your repository, click **Add file**, **Upload files**, and drag in the new `index.html`, `404.html`, `robots.txt`, `favicon.svg`, `apple-touch-icon.png` and `og-image.png` and the `licences` folder, then open the `pipeline` folder in the zip and upload the new `update_prices.py`, `site_address.py` and `config.json` into your repository's `pipeline` folder (and `tests/run_tests.py` into `pipeline/tests`). **Do not upload `prices.json`**, because yours holds the latest prices. Commit. Then redo step 4 with the new `update-prices.yml`: open `.github/workflows/update-prices.yml` in GitHub, click the pencil icon, select everything, paste over it the text of the new `github-workflow/update-prices.yml`, and commit. Then go to step 10. **You should see** the **Run workflow** box now has two choices, **mode** and **scope**.
3. Back on GitHub, click **uploading an existing file**.
4. Select **everything inside** `plateful-auto` (not the folder itself, and not the zip) and drag it onto the GitHub page. **Leave out the `price-checker` folder**: it runs on your computer and does not belong on GitHub. Dragging folders works in Chrome, Edge and Firefox.
5. Wait for the file list to finish loading.
6. Scroll down and click the green **Commit changes** button.

**You should see:** your repository's main page listing `index.html`, `404.html`, `prices.json`, `robots.txt`, the three picture files, `README.md`, `pipeline`, `github-workflow` and `licences`.

**If a folder is missing:** click **Add file**, **Upload files**, and drag the missing folder in on its own. Then commit again.

### Step 4. Create the robot's instruction file

GitHub only runs robots from a hidden folder called `.github/workflows`. A hidden folder can't be dragged in, so you create this one file with GitHub's own editor.

1. On your repository page, open the folder `github-workflow`, then click the file `update-prices.yml`.
2. Click the **copy** icon (two overlapping squares) at the top right of the file view. This copies the whole file.
3. Go back to the repository's main page. Click **Add file**, then **Create new file**.
4. In the box that says **Name your file...**, type exactly: `.github/workflows/update-prices.yml`
   Typing the `/` makes GitHub turn each part into a folder. You'll see `.github` then `workflows` appear as you type.
5. Click in the big editor area and paste (Ctrl+V on Windows, Cmd+V on Mac).
6. Click the green **Commit changes...** button at the top right, then **Commit changes** in the box that opens.

**You should see:** the repository now has a `.github` folder, and clicking the **Actions** tab at the top shows a workflow called **Update prices** in the left list.

**If the Actions tab says workflows are disabled:** click the green button to enable them.

**If the name box won't let you type a dot at the start:** check you clicked **Create new file**, not **Upload files**.

### Step 5. Allow the robot to save its results

1. Click **Settings** (the tab at the top right of your repository).
2. In the left menu click **Actions**, then **General**.
3. Scroll to **Workflow permissions**, choose **Read and write permissions**, and click **Save**.

**You should see:** a short "saved" message at the top of the page.

**Why:** without this the robot can fetch prices but GitHub refuses to let it save them, and the run fails with "Resource not accessible by integration".

### Step 6. Turn on the website (GitHub Pages)

1. Still in **Settings**, click **Pages** in the left menu.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Under **Branch**, choose **main** and **/ (root)**, then click **Save**.
4. Wait about two minutes, then refresh the page.

**You should see:** a banner at the top saying **Your site is live at** followed by an address like `https://yourname.github.io/plateful/`.

**If there is no banner after ten minutes:** check the Branch box really says `main` and `/ (root)` and that you pressed Save. If your branch is called `master` instead, pick that.

5. On the same Pages screen, scroll down to **Enforce HTTPS** and make sure the box is ticked. This makes every visit use the secure `https://` form of the address.

**You should see:** a tick in the **Enforce HTTPS** box. On a new `github.io` site it is normally ticked already.

**If the box is greyed out and says the certificate is not ready:** wait up to an hour and look again. GitHub is still issuing the security certificate. The site also moves visitors to `https://` by itself, so nothing is unsafe in the meantime.

### Step 7. Look at the website

1. Click the address from step 6.

**You should see:** Plateful, with the coin-toss intro and the search box. Search for "spaghetti bolognese", click **Compare prices**, and you should see prices with small green "live" tags on the ingredients that have real prices.

Three more things to check while you are there:

- The browser tab shows a small plate icon. **If it shows a blank page icon:** check `favicon.svg` was uploaded in step 3.
- At the bottom of the page there are **Privacy** and **Terms of use** links, and each opens its page. **If they are missing:** the `index.html` on GitHub is an older copy, so upload the new one again.
- Add `/nothing-here` to the end of the address and press Enter. **You should see** a page headed "Nothing on this plate" with a **Go to the recipes** button. **If you see GitHub's own plain 404 page instead:** check `404.html` was uploaded in step 3.

**If you see a GitHub "404" page at the real address:** give it up to ten minutes, then try again. **If the page loads but looks unstyled or blank:** tell me what you see and which browser you use.

This is your new address. The old claude.ai link still works but it is a frozen copy and will not update itself.

### Step 8. Get your Apify token

You already have an Apify account from earlier.

1. Go to **console.apify.com** and sign in.
2. Open **Settings** (bottom of the left menu, or under your profile picture), then **API & Integrations**.
3. Click **Create a new token**, name it `plateful-github`, and copy the token.

**You should see:** a long string of letters and numbers that you can copy.

**If you can't find it:** Apify moves menus around from time to time. Search Apify's help for "API token" and look for the page that lists your personal API tokens.

**Keep the token private.** Don't paste it into a chat, a file or a public page. Anyone holding it can spend your Apify credit. Step 9 puts it somewhere safe.

### Step 9. Give the token to GitHub as a secret

1. In your repository click **Settings**, then **Secrets and variables** in the left menu, then **Actions**.
2. Click **New repository secret**.
3. **Name:** `APIFY_TOKEN` (capital letters, exactly like that).
4. **Secret:** paste the token.
5. Click **Add secret**.

**You should see:** `APIFY_TOKEN` in the list of repository secrets. GitHub never shows the value again, which is normal.

**If you made a typo in the name:** delete the secret and add it again. The name must match exactly.

### Step 10. Run the test (50 cents at most)

1. Click the **Actions** tab.
2. Click **Update prices** in the left list.
3. Click **Run workflow** (a grey button on the right), leave **Branch: main**, set **mode** to **test**, and click the green **Run workflow**.
4. Refresh after a few seconds and click the new run that appears. It takes about 5 to 10 minutes.

**You should see:** a yellow spinning dot while it runs, then a green tick.

5. When it's green, go back to the repository's **Code** tab and open `pipeline`, then `last-run-report.md`.

**You should see, near the top, a table like this:**

| Shop | Searches ok | Failed | Returned nothing | Ingredients matched | Used this run? |
|---|---|---|---|---|---|
| Aldi | 8 | 0 | 0 | 6 | yes |
| Lidl | 8 | 0 | 2 | 3 | yes |
| Morrisons | 8 | 0 | 0 | 6 | yes |

(Your numbers will differ. What matters is **"Used this run?" says yes for each shop** and there are some matched ingredients.)

Below that, **What it picked** lists the exact product chosen for each pack, and **Searched but nothing usable found** shows the nearest rejected products and why.

**If a shop says `NO` in the last column, or matched is 0:** don't go further yet. Send me the contents of `last-run-report.md`, and if you can, the files in the `pipeline/samples` folder. Those show exactly what the shop's robot returned, and I'll adjust the rules. Expect to do this at least once for Lidl in particular: its robot doesn't document its output, so the first test is how we find out what it really returns.

**If the run shows a red cross:** click it, then click the step with the red cross, and read the last lines. The common ones:

- "Apify refused the token": the secret is wrong or missing. Redo step 9 with a fresh token.
- "out of credit": top up or upgrade in Apify (Settings, then Billing).
- "Resource not accessible by integration": redo step 5.
- "APIFY_TOKEN is not set": the secret name in step 9 doesn't match exactly.

**The test run also tells the site its own web address.** Link previews (the picture and title that appear when someone shares the site in a message), the sitemap for search engines and the "Nothing on this plate" page all need the site's full address, and the robot works it out from your repository's name. **You should see**, on your repository's main page after the run, a new file called `sitemap.xml`. **If it is not there:** open the run, click the step **Tell the site its own web address** and tell me what it printed. Until this has run once, sharing the site's link still works but shows no picture.

### Step 11. Check the picks look sensible

Read through **What it picked** in the report.

**You should see** plain, everyday products at believable prices, for example an ordinary 500g beef mince from each shop, not an organic or flavoured version.

**If something looks wrong** (a flavoured product, a wrong size, a strange price), send me that line. The fix is usually one line in `pipeline/config.json`.

### Step 12. Run it for real (about $9 at the very most)

Do this once you're happy with the test. This first run searches **every** ingredient so the whole site gets live prices (later Monday runs only do the ingredients that are due).

1. Actions tab, **Update prices**, **Run workflow**, set **mode** to **live** and **scope** to **all**, **Run workflow**.
2. It takes roughly 30 to 60 minutes. You don't need to keep the page open.

**You should see:** a green tick, and a new entry in the repository's commit list saying "Update prices (live run...)".

3. Wait a few minutes, then open your website address and do a **hard refresh** (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac).

**You should see:** far more ingredients with green "live" tags, and a footer that says the latest check date is today and that prices are refreshed automatically.

4. In Apify, open **Billing** or **Usage** and look at what this run cost. That is your real price per full run. If it is higher than you want, see step 13.

**If the website still shows old prices after ten minutes:** open `prices.json` on GitHub and check its date near the top. If it's today's date, it's just the browser or GitHub's cache: wait a bit and hard refresh again. If it's not, open the run on the Actions tab and read the last lines.

### Step 13. (Optional) Put a cap on spending, or choose fewer shops

**A spending cap.** In Apify, open **Settings**, then **Limits** (or **Billing**) and set a monthly usage limit, for example $25. The robot also stops itself if a single run would cost more than about $12.

**Fewer shops (the easy way to save money).** Morrisons costs about four times as much to search as Aldi. To search only Aldi and Lidl:

1. In your repository click **Settings**, **Secrets and variables**, **Actions**, then the **Variables** tab, then **New repository variable**.
2. **Name:** `SHOPS`   **Value:** `aldi,lidl`
3. Click **Add variable**.

**You should see:** `SHOPS` in the variables list. From the next run, only those shops are searched, and Morrisons keeps whatever price it had. To go back, delete the variable.

**Refreshing less often.** Each ingredient in `pipeline/config.json` has a `"refresh"` number. Leave it out (or 1) for every week, 2 for every second week, 4 for every fourth week. Changing the 2s to 4s makes things cheaper but the prices get older. Ask me and I'll do it for you.

### Step 14. Switch on the automatic schedule (weekly, every 2 days or daily)

Only do this when steps 10 to 12 worked.

**First choose how often.** More often catches offers sooner but costs more, because Apify charges for every search. These are worst-case monthly figures from the robot's own estimate (real runs usually cost less, and step 12 shows you the real cost of one run):

| How often | Value to type | Aldi + Lidl | Aldi + Lidl + Morrisons |
|---|---|---|---|
| Every Monday | `weekly` | about $11 a month | about $26 a month |
| About every 2 days (Mon, Wed, Fri, Sun) | `every2` | about $33 a month | about $79 a month |
| Every day | `daily` | about $55 a month | about $133 a month |

On the extra days only the 89 everyday ingredients are searched (milk, bread, mince, veg and so on). Spices, tins and other cupboard items stay on their weekly or monthly turn, because their prices rarely move. To use only Aldi and Lidl, add the `SHOPS` variable from step 13.

1. In your repository click **Settings**, **Secrets and variables**, **Actions**.
2. Click the **Variables** tab, then **New repository variable**.
3. **Name:** `AUTO_UPDATE`   **Value:** `weekly`, `every2` or `daily` (from the table above). The older value `on` still works and means weekly.
4. Click **Add variable**.

**You should see:** `AUTO_UPDATE` with your chosen value in the variables list.

From now on it runs at about 05:17 UTC (6:17 am UK summer time) on the days you chose. On days that are not run days the job still appears on the Actions tab for a few seconds with a green tick and does nothing; that is normal and costs nothing. To change how often, edit the variable. To switch it off, delete the variable. Nothing else will bill you.

**You should see, after the first scheduled run:** a new commit "Update prices (live run, ...)", and the site's footer saying everyday items are refreshed every day or every 2 days.

**If the bill is higher than you want:** set a monthly limit in Apify (step 13), add `SHOPS` = `aldi,lidl`, or change `daily` to `every2`.

**If GitHub ever emails you that the schedule was paused:** GitHub pauses schedules on repositories with no activity for 60 days. The weekly price saves count as activity, so this shouldn't happen, but if it does, open the Actions tab and click **Enable workflow**.

---

## Home price checker (free, runs on your own computer)

This is the no-Apify way to get live prices. A small program in the `price-checker` folder runs on your own computer. It opens a normal browser window, looks up each Plateful ingredient on the **Tesco, Sainsbury's, Morrisons and Lidl** websites one page at a time (a few seconds apart), reads the prices shown, and saves the new `prices.json` straight to your GitHub repository. Your website then shows those prices within a few minutes. It costs nothing to run.

**What it reads.** The normal price, the "was" price (shown on the site as a sale), and the loyalty-card price (Clubcard, Nectar, More Card, Lidl Plus), which the site shows to people who tick that card. It uses the same matching rules as the Apify robot (`pipeline/config.json`), so it ignores organic, flavoured, wrong-size and ready-meal versions.

**What it does not do.**
- It does not visit Aldi, Asda, Waitrose or Iceland. Their websites' robots.txt rules ask automated programs not to visit their product pages, so those shops keep their estimated prices (or the last checked ones).
- It does not try to get round anything a shop puts in the way: no hidden tricks, no fake identities, no "I'm not a robot" solving, and it does not click cookie banners. If a shop refuses a visit, that shop is stopped for the rest of the run, its old prices are kept, and the report says so.
- It only runs while your computer is on. A full run takes roughly 40 to 60 minutes; an everyday-items run roughly 30.

**Please note.** Shops' website terms of use often say their sites should not be used for automated price collection, and a shop can block it or change its pages at any time. Whether you use this is your decision. Prices on shop websites can also differ from what you pay in store.

**Before you start:** do steps 1 to 7 above (GitHub account, repository, files uploaded, website switched on). You do **not** need steps 8 to 14 (Apify) for this.

### Checker step 1. Put the folder somewhere permanent

Unzip the package and move the whole `plateful-auto` folder to a place it will stay, for example your **Documents** folder.

**You should see:** inside `plateful-auto`, a folder called `price-checker` containing `check_prices.py`, `settings.json` and several files ending in `.command` (Mac) and `.bat` (Windows).

**If you later move the folder:** run the schedule file again (checker step 8), because the schedule remembers where the folder was.

### Checker step 2. Check you have Python 3

- **Mac:** open **Terminal** (press Cmd+Space, type Terminal, press Enter), type `python3 --version` and press Enter.
- **Windows:** open **Command Prompt** (press the Windows key, type cmd, press Enter), type `py --version` and press Enter.

**You should see:** something like `Python 3.12.4`. Any version from 3.9 up is fine.

**If it says the command is not found** (or a Mac asks to install "command line developer tools"): install Python from **python.org** (Downloads, then the big yellow button). On Windows, tick **"Add python.exe to PATH"** on the first screen of the installer. Then close and reopen Terminal or Command Prompt and try again.

### Checker step 3. Run the one-time setup

- **Mac:** in the `price-checker` folder, **right-click** `setup-mac.command` and choose **Open**, then **Open** again in the box that appears. (The right-click is only needed the first time each file is opened, because it was downloaded from the internet.)
- **Windows:** double-click `setup-windows.bat`. If a blue "Windows protected your PC" box appears, click **More info**, then **Run anyway**.

**You should see:** a window with installation text, ending with **SETUP FINISHED**. It can take a few minutes.

**If it ends with SETUP FAILED:** copy the text in the window and send it to Claude.

### Checker step 4. Tell it your repository

Open `settings.json` in the `price-checker` folder with a plain text editor (Mac: right-click, Open With, TextEdit; Windows: right-click, Open with, Notepad). Change only the text between the quotes:

- `"github_repo"`: your GitHub name and repository name with a slash between, for example `"noah123/plateful"`. It's the part after `github.com/` in your repository's web address.
- `"how_often"`: `"daily"` or `"every2"` (every 2 days).
- `"shops"`: remove any shop you don't want checked (keep the quotes and commas tidy).

Save the file.

**You should see:** the file still starts with `{` and ends with `}`, with your repository name in place of `YOUR-GITHUB-NAME/YOUR-REPOSITORY-NAME`.

### Checker step 5. Make a GitHub token (a key that lets the checker save prices.json)

1. On github.com, click your profile picture (top right), then **Settings**.
2. At the bottom of the left menu click **Developer settings**, then **Personal access tokens**, then **Fine-grained tokens**, then **Generate new token**.
3. **Token name:** `plateful price checker`. **Expiration:** 90 days (or longer, up to a year).
4. **Repository access:** choose **Only select repositories** and pick your Plateful repository.
5. **Permissions:** open **Repository permissions**, find **Contents** and set it to **Read and write**. Leave everything else as it is.
6. Click **Generate token** and copy the token (it starts with `github_pat_`).

Now save it in a file **in your home folder** (not in the Plateful folder, so it can never be uploaded by accident):

- **Mac:** open **TextEdit**, choose **Format, Make Plain Text**, paste the token, then **File, Save**. Name it `plateful-github-token.txt`. In the save box press **Cmd+Shift+H** to jump to your home folder, then **Save**. If it asks about the ".txt" ending, choose **Use .txt**.
- **Windows:** open **Notepad**, paste the token, **File, Save as**. Go to `C:\Users\` and open the folder with your name. Name it `plateful-github-token.txt`, set **Save as type** to **All files**, and click **Save**.

**You should see:** a file called `plateful-github-token.txt` in your home folder containing just the token on one line.

**Keep it private.** Never paste it into a chat (including with Claude), an email or a GitHub page. If it ever leaks, delete it on the same GitHub page and make a new one. When it expires, GitHub emails you; make a new one the same way and replace the file's contents.

### Checker step 6. Do a trial run (8 ingredients, nothing saved)

- **Mac:** right-click `test-mac.command`, **Open**.
- **Windows:** double-click `test-windows.bat`.

**You should see:** a browser window open and visit the shops' search pages by itself for 2 or 3 minutes. **Leave it alone** until it closes. Then the text window says **Trial finished**. A new `work` folder appears inside `price-checker`; open `work/last-run-report.md` in your text editor.

**In the report you should see** a table near the top with a line per shop. What matters is **"Used this run?" says yes** and there are some matched ingredients. Below it, **What it picked** lists the products chosen.

**If a shop says NO, or matched is 0:** send Claude the report (and, if you can, the files in `work/samples`). Shops lay their pages out differently, so expect to do this at least once. The fix is usually small.

**If the window says GitHub refused the token, or could not find a file:** redo checker step 4 (the repository name) or step 5 (the token).

### Checker step 7. The first real run

- **Mac:** right-click `run-now-mac.command`, **Open**.
- **Windows:** double-click `run-now-windows.bat`.

It takes roughly 40 to 60 minutes. Leave the browser window alone; you can use other programs meanwhile.

**You should see** at the end: **New prices saved to GitHub**, then **Done**. On GitHub, your repository shows a new change "Update prices (home checker, ...)". A few minutes later, open your website and do a hard refresh (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac).

**On the website you should see** green "live" tags on many more Tesco, Sainsbury's, Morrisons and Lidl prices, and today's date in "About these prices".

**If it says "No prices changed":** nothing matched or a shop refused. Read `work/last-run-report.md` and send it to Claude.

### Checker step 8. Make it run by itself every morning

- **Mac:** right-click `schedule-mac.command`, **Open**.
- **Windows:** double-click `schedule-windows.bat`.

**You should see:** **SCHEDULED**. From now on it starts at 07:30 every morning. With `"how_often": "every2"` it does nothing on the in-between days. On Mondays (or if a week has passed) it checks all the ingredients due that week; on other run days only the everyday ones.

Things to know:
- Your computer has to be on (a Mac that is asleep at 07:30 runs it when it wakes). A browser window will open during the run; leave it until it closes.
- Each run writes `work/checker-log.txt` (a line per run) and `work/last-run-report.md`. The report is also copied to `pipeline/last-run-report.md` on GitHub, so you can read it from your phone.
- To stop it: `unschedule-mac.command` or `unschedule-windows.bat`.

**If nothing happens at 07:30:** open `work/checker-log.txt`. If it is empty, run the schedule file again. On Windows you can also open **Task Scheduler** and look for "Plateful price check".

**Do not upload the `price-checker/work` or `price-checker/browser-profile` folders to GitHub.** They are only for your computer.

## Things worth knowing

**How often each ingredient is refreshed.** The 89 everyday ingredients are refreshed every week, or every 2 days or every day if you chose that in step 14. The 96 added later (fresh meat and veg, dairy, bread: every second week; spices, oils, sauces, tins, flour and sugar: every fourth week) are spread across the weeks, so each Monday only about two thirds of the ingredients are searched. This is what keeps the cost down. A price can therefore be up to 4 weeks old; the footer shows the latest check date and each product's own check date is stored in `prices.json`. A sale is shown for a week after the run that found it and then switches off, unless a later run finds it again (with every-2-days or daily runs, an everyday item's sale is checked again within a day or two).

**Ingredients you add to recipes yourself.** People can type any ingredient into their own recipe. If it matches one of the food products in the price list it is priced; otherwise it is shown in the recipe and on the shopping list as "not priced" and left out of the totals, so nobody is told a wrong price. Share links work on the GitHub page above; they may not work if the site is opened inside a preview pane, but pasting the recipe code always works.

**The recipe pictures are drawn by the page itself.** There are no picture files to upload or keep up to date: each dish (including your own recipes) is drawn in a flat, hand-drawn cartoon style when the page opens, so it works offline and costs nothing.

**The answer comes first.** At the top of each recipe, and of My shop, a card shows the cheapest total at one shop next to the cheapest total if you split the shop between several (each shop with its subtotal, and the products to buy there as a bulleted list with their prices; the one-shop card lists everything you would buy at that shop too). Under it is a short "About these prices" section holding the long explanations; the full tables (cost at each shop, cheapest basket, ingredient comparison) are all still on the page below. My shop is in the top menu with a count of the meals in it.

**Budget.** The "Budget" page in the top menu (also reachable from the home page) asks what you can spend on one meal and shows every recipe that fits, cheapest first. Each card shows the price and names the cheapest shop to buy it from, and how much of the budget is left over. People can type any amount up to £500 or tap a quick amount (£3, £5, £8, £10, £15), and change how many people they are cooking for and their dietary needs; the list re-prices straight away. By default a recipe counts as fitting if everything can be bought at one supermarket for the budget or less. The "Split between shops" choice uses the cheapest mix of shops instead, which lets a few more recipes in and names each shop to visit. Under the list, "Just over your budget" shows the four nearest misses and how far over each one is. Opening a recipe from this page shows the usual full comparison (cheapest single shop, cheapest split, cost at every shop), plus one line saying whether it fits the budget and how much is left, and a "Back to budget" link. Prices use the shops the person has ticked and count whole packs, like the rest of the site, and the same live and estimated prices. The budget amount is not saved: it lasts only while the page is open, and the page opens with a £10 example.

**Weekly budget.** On the Budget page, "The whole week" lets people set what they can spend on food for the week (any amount up to £500, or tap £20, £30, £40, £50 or £60). The meals they add are the ones in My shop, so the running total is the real cost of buying them together: an ingredient used in two meals is paid for once. Each recipe card shows what it would add to the week, and "Only what fits" hides the recipes that would take them over. When the week goes over the budget the page says "Over budget by £x" in the running total, in the message that pops up, on My shop and in the bar at the bottom of the other pages, with a tip on getting back under. People's own recipes are in the list too, and "Add your own recipe" on that page comes back to the week. A week can hold up to 21 meals. The weekly budget is saved in the visitor's own browser only.

**124 recipes, by meal.** There are 124 recipes (there were 43 to begin with): breakfasts, lunches and dinners, from a 5-minute microwave mug omelette to a roast chicken dinner. A picker at the top of the Recipes and Budget pages shows All, Breakfast, Lunch or Dinner. Some recipes suit two meals, and each recipe page says which.

**What's in your kitchen.** Under the meal picker, people tick the appliances and pans they have (hob, oven, grill, microwave, air fryer, toaster, kettle, blender, slow cooker, saucepan, frying pan, baking tray, oven dish). The pages then show only the recipes they can cook with that. Recipes know their alternatives: crispy chicken and chips needs an air fryer, or an oven and a tray. Nothing ticked means everything shows. A recipe opened by searching says what is missing ("This needs an oven and an oven dish, which you have not ticked"). The ticks are saved in the visitor's own browser only.

**The kitchen list is strict (changed 6 October 2026).** With something ticked, the list is only the recipes that kit actually cooks. Tick only "Slow cooker" and you get the three slow cooker recipes (pulled chicken, beef stew, sausage and bean casserole), not the twelve sandwiches and salads that used to be mixed in. Recipes that need no cooking, and people's own recipes (the site cannot know what those need), are behind a tick box in the kitchen box: "Also show the 12 recipes that need no cooking, or are your own". Appliances and pans are judged separately: if someone ticks appliances but no pots and pans, the site takes it they have the pans, and the other way round. Before this, ticking only "Hob" showed no hob recipes at all, because no pan was ticked. The beef stew no longer needs a kettle and the sausage casserole no longer needs a hob (browning the sausages is optional), so a slow cooker alone is enough for both.

**Customise to your needs: fitness goals (added 6 October 2026).** The box at the top of the Recipes and Budget pages is now headed "Customise to your needs". Beside "Which meal?" there is "Fitness goal (optional)": No goal, High protein, Lose fat, Maintain, Build muscle or Low carb. Picking one shows only the recipes that suit it, best first (most protein, fewest calories, closest to 550 kcal, or fewest carbs), and each card then shows the calories and protein in a serving. "Cheapest first" and "Quickest first" still work on the shorter list, and the goal works together with the meal picker and the kitchen box. The rules, which the page states under the picker: High protein is 25g of protein or more in a serving with at least a fifth of its calories from protein (39 of the 124 recipes); Lose fat is 500 kcal or less (63); Maintain is 400 to 700 kcal with 15g of protein or more (74); Build muscle is 30g of protein or more and 550 kcal or more (24); Low carb is 35g of carbohydrate or less (15). Every recipe page shows the calories, protein, carbs and fat in a serving under its title, and says whether the recipe fits the chosen goal (the full panel is described below). People's own recipes get the same line, worked out from the ingredients the site knows (it says so when some were typed in by hand and could not be counted).

**Nutrition from pack labels (7 October 2026).** Every recipe page has a nutrition panel laid out like the table on a UK pack: energy, fat, saturates, carbohydrate, sugars, fibre, protein and salt, for one serving, as a share of an adult's daily reference intake (% RI), and for all the servings being cooked. Change the Serves buttons, an amount or an ingredient and the panel, the four headline figures under the title and the "All 4 servings" total all move with it. A bar shows where the calories come from (protein, carbs, fat). The sums use exactly what the ingredient list shows (so 1 onion for 2 people counts as a whole onion), the oil, sugar and honey measured in the method, and only the part of a loaf that is eaten (2 slices each, not the whole loaf). The figures for the 203 products the recipes use (the 171 ingredients plus their swaps) were read from the nutrition labels of Tesco own-brand packs on tesco.com on 7 October 2026: 158 came straight from a label, and 45 use standard figures for the raw or dry food because the label only gives a "cooked" column (dried pasta, rice, sausages and so on). The other 299 products, which only come up in people's own recipes, use standard typical figures. Tins in water count the drained weight, and fruit and veg count the edible part. They are still a guide: brands differ, and "a pinch of salt" is not counted. The Terms page says so and says it is not dietary or medical advice.

**Recipes re-checked (7 October 2026).** All 124 recipes were gone through again the way a recipe tester would: the order of the steps, every time and temperature, the ratios (rice to water, stock, batters), the amounts for 4 people, and UK food safety. 66 had their total time corrected, nearly all upwards, because the old figure was shorter than the method's own steps for a beginner (a fry-up is 45 minutes, not 30; a roast chicken dinner is 125, not 105). Oven temperatures now read "200°C (180°C fan, gas 6)". Each recipe page now also has a line saying what the dish is, the prep time and the cooking time, whether it is easy or more effort, how many days it keeps in the fridge and whether it freezes.

**Amounts in the method.** The steps used to say "add the mince". They now say "add 500g of beef mince" and "heat 1 tbsp of oil", and the amounts follow the Serves buttons: 1kg and 2 tbsp for 8 people, 250g and 1½ tsp for 2. Oil is always measured (and counted in the nutrition). If someone changes an amount, swaps an ingredient or takes one out, the method follows (a removed ingredient's amount is struck through). Small amounts in the ingredient list carry a spoon measure ("30g, about 2 tbsp"). Times do not scale, so the page says they are for 4. "Make my own version" copies the method with the amounts written out.

**The look (7 October 2026).** A redesign so the site reads as a food app: a green masthead on the home page with the logo, the search and three dishes; the sections as plain text tabs with a yellow marker (on a phone, a tab bar with icons fixed to the bottom of the screen); recipe cards that lead with the picture, each on one of six table-top colours, with the price for 4 and for each serving; the "What's in your kitchen?" box folded away until it is opened so the food shows sooner; and a recipe page that opens with the picture, the description and the facts, with the method at full width under the ingredients and prices. Colours, type and logo are unchanged in spirit (bottle green, shelf-label yellow, Archivo), light and dark.

**Shopping list in one place (7 October 2026).** "Make shopping list" on a recipe or on My shop still shows the list on the page, and now also puts everything on the Shopping list tab, so one list tracks it all. There is a quicker way too: "Add to shopping list" on every recipe page, and in the bar at the bottom of the screen whenever My shop has meals in it (one press sends the whole shop to the list and opens it). Pressing a button twice does not double the amounts. On the Shopping list tab, **Finished shop** saves the list, the meals it was for and the cheapest price found to the Previous page and to "What you've spent" on the Budget page, then clears the list and My shop ready for next time.

**Favourites, planner and Previous (7 October 2026).** Every recipe card and recipe page has a heart, and the Favourites page shows the recipes that have one. The Meal planner has the seven days of the week: add recipes to a day (favourites are offered first), give each its own number of servings, mark one as cooked, and send the whole week to My shop with the servings added up. The Previous page lists the meals you have had (from "I've cooked this", "Cooked" in the planner, or a finished shop) and the shops you have done, each with its date, what was on it and what it came to. All of it is saved in the visitor's own browser only, is listed on the Privacy page and is removed by "Delete everything saved". With nine sections, a phone shows Recipes, My shop, List, Planner and a More button that opens the rest.

**Servings per recipe.** A recipe that is in My shop shows its own servings buttons on its card, so one meal can feed six while the rest feed four. The planner has the same buttons on every planned meal.

**Fuller pictures.** The food is drawn larger, the plate fills more of its frame, there is a napkin and a table under it, and the empty patches measured on 59 plates are filled with more of the dish's own food (more chips, another hash brown) or with salad leaves or berries. Recipe names on the cards are larger.

**Planner, Previous and Favourites (7 October 2026).** Three new sections. *Planner*: the seven days of the week, each with the recipes planned for it and each recipe with its own number of servings; "Add the week to my shop" sends them all to My shop to be priced, "Cooked" moves one to Previous. A recipe page can plan itself for a day. *Previous*: the meals you have had and the shops you have done, newest first, with what each shop cost and what was on it; "Have it again" puts a meal back in My shop. *Favourites*: every recipe card and recipe page has a heart, and the Favourites page shows the recipes with one. On a phone the tab bar is Recipes, My shop, List, Planner and More (Favourites, Previous, Leftovers, Budget, Saved).

**A quicker shopping list.** "Make shopping list" on a recipe or on My shop now also puts the ingredients on the Shopping list tab, so everything is tracked in one place (pressing it twice does not double the amounts). The bar at the bottom of the screen has an "Add to shopping list" button that sends everything in My shop to the list and opens it, and a recipe page has one for that recipe. The Shopping list tab has "Finished shop": it saves the list and the cheapest price found for it to Previous and to a "What you've spent" section on the Budget page (last 7 days, this month, and against the weekly budget if one is set), then clears the list and My shop.

**Servings for each recipe.** A recipe that is in My shop shows its own servings buttons on its card, so one meal can feed more people than the rest. Planned meals have the same.

**Smaller changes.** Recipe names on the cards are bigger. Pictures: each dish's food is drawn at a scale measured for it so that it covers most of the plate (72 dishes measured, plate cover up from 61% to 76% on average), the plate fills more of its frame, and there is a napkin, a table line and a grind of pepper. All of this is kept in the visitor's own browser under one name (`plateful-life`), listed on the Privacy page and removed by "Delete everything saved".

**Search button.** The Search button beside the search box on the Recipes page does the same as pressing Enter: it opens the recipe that was typed.

**How much you have saved.** Each item on the Shopping list has a "Bought" tick box, and a "Where are you buying it?" box (the cheapest single shop, the cheapest shop for each item, or a named shop). Ticking an item notes what it cost at that shop and the average price of the same item across the shops the visitor has ticked. The "Saved" tab opens the page "How much you have saved", which shows this month's saving, the total, and a month-by-month table of what was spent and saved. A month spent at a dearer-than-average shop says "£x more" instead of claiming a saving. Unticking takes an item back off. Only the monthly totals are kept, in the visitor's own browser, and there is a "Clear my savings history" button. Because many prices are estimates, the page says the figures are a guide.

**Ticks on recipe shopping lists count too.** The shopping list you make from a recipe, or from My shop ("Make shopping list"), has a tick box for each item. Ticking one adds it to "How much you have saved": what it costs at the shop that list sends you to, against the average across the ticked shops. The ticks are kept in the visitor's own browser for a week, so a reload does not lose them and nothing is counted twice. "Clear the ticks" empties the boxes for the next shop and keeps the savings. Unticking takes an item back off.

**Tick all.** Every shopping list has a "Tick all" button: the list on a recipe page, the list in My shop, and the Shopping list page. It ticks every item at once and becomes "Untick all".

**M&S.** M&S is the ninth supermarket. It is in the "Shops near you" list, the price tables and the nearest-shops list (about 1,000 M&S food shops, with the small ones in petrol stations, motorway services, railway stations and hospitals marked as small shops; clothing-only and outlet shops are left out). **All M&S prices are estimates.** M&S is not one of the shops the weekly robot checks, and it has no loyalty-card prices on the site. Anyone who had already chosen their shops before M&S was added gets M&S ticked once, and can untick it.

**Save changes on a recipe.** On a recipe page, taking an ingredient out, changing an amount, swapping an ingredient or adding one makes a "Save changes" button appear under the ingredients. Pressing it saves that version in the visitor's own browser, so the recipe opens that way from then on, and the recipe card, My shop and the budget are priced from it too. Anything taken out stays under the ingredients in a greyed-out "Taken out" box with an "Add back" button, and the steps say which ingredient to skip. "Undo" drops changes that have not been saved, and "Reset to the original recipe" puts a saved recipe back as it was written. On a recipe the visitor added themselves, Save changes rewrites that recipe.

**Fuller cooking instructions.** Every one of the 124 recipes now has 6 to 12 steps (4 or more when there is no cooking). Each step has a short title and says how to prepare each ingredient, what heat to use, how long for, what to look for and how to tell the food is done. Recipes that can be cooked another way (air fryer, microwave, grill) have a step for it. Under the steps a "Good to know" box gives 2 to 4 tips: how to store and reheat leftovers safely, swaps, common mistakes and getting ahead. **The times and temperatures are general guidance and have not been kitchen-tested.**

**Fuller pictures.** Spaghetti and noodles are drawn as a full, twirled pile instead of thin separate strands. About 70 dishes were redrawn or added to so the plate is not half empty: curries sit on a bed of rice, fish and chips has a proper pile of chips and peas, sandwiches are cut into three, wraps and burgers fill the board, traybakes are crowded, soups and bakes have more on top, and pies have fork marks. On average 60% of each plate was covered with food before and 70% is now, and the number of sparse pictures (under 40% covered) went from 50 to 3.

**Write your recipe.** The "Add your own recipe" page has a "Write your recipe" button. It opens a writing space with a Steps box (one step per line) and a Notes box (oven temperature, what to serve it with, who gave you the recipe). Both are saved with the recipe in the visitor's own browser, shown on the recipe's page and included in its share link. An own recipe with nothing written yet shows the same button on its page. "Make my own version" of one of the site's recipes copies its steps and puts its tips in the notes.

**The name.** The site is called Plateful. It was renamed Platefull on 6 October 2026 and changed back to Plateful on 8 October 2026: the page title, both drawn logos (back to eight letters), the footer, the Privacy and Terms pages, the link-preview picture and the 404 page all say Plateful again. The folder and file names in this package (`plateful-auto`, `plateful-open-in-browser.html`) and the names the site saves things under in the browser never changed, so nothing a visitor had saved is lost.

**Feedback section (waiting for a link).** A "Tell me what you think" section with a "Give feedback" button is built into the bottom of every page, but it stays hidden until the site is given the link to a Google Form. Send me the form's link and I'll switch it on. The button opens the form in a new tab; the Privacy page then explains that the form is run by Google.

**Build your own shopping list.** The "Shopping list" page in the top menu (after My shop) lets you search all 526 products (or browse them by shelf), tap to add them, set how much of each you need, and see the cheapest single shop and the cheapest split across several shops, in the same answer card as the recipe pages. Each item is one standard pack to begin with, and the list is saved in your own browser only (no account, no share link). It uses the same shops, postcode and loyalty-card box as the rest of the page; on a wide screen that box sits beside the answer, and on a smaller screen it goes under the list. Only products in the 184-item list can be added.

**The product list.** The site lists 526 products: the 184 original cooking ingredients plus 342 newer ones (more fresh fruit, veg, meat, fish, cheese and baking items, tins, jars, sauces and spices; breakfast foods, drinks and snacks; frozen and ready-made food; and 24 household and toiletries items). They are grouped into 17 shelves in the "Browse all products" list on the Shopping list page. Household and toiletries items can only be added on the Shopping list page: they never show up in recipes or Leftovers. **The 342 newer products show estimated prices only (my own figures, nudged by how far my figures were out in each aisle once the real prices were checked).** The weekly robot still checks just the 184 original ingredients, so the cost above has not changed. Adding the newer products to the robot's checks would roughly triple the number of searches (worst case about $65 a month instead of $26), so it is switched off until you decide you want it; the site marks every price that was not checked online, so nobody is told an estimate is a checked price. The robot simply skips any product that has no rules block in `pipeline/config.json`, so the weekly run does not fail because of them. To start checking one later, add a rules block for it to that file (copy a similar ingredient) and run `python pipeline/update_prices.py --check-config`.

**Leftovers use the same prices.** The "still need" prices on the Leftovers tab come from the same price list, so they are only as live as the ingredients in them (see the next point). Leftovers you type that aren't in the food price list are kept as notes and only used for the quick ideas.

**Real prices checked on 5 and 6 October 2026.** I looked up all 171 recipe ingredients (and 50 other products) on the Tesco, Sainsbury's and Morrisons websites, the three shops whose sites allow it. 200 products now have a real price at one or more of those shops (153 of the 171 recipe ingredients, 105 of them at all three): 174 at Tesco, 177 at Sainsbury's, 170 at Morrisons, 593 pack prices in all, with 25 Clubcard, Nectar or More Card prices. For each pack size the pick is the cheapest plain own-label item, budget ranges included (Hearty Food Co., Stamford Street Co., Savers), never organic or premium. These show the green "live" tag with their check date. Tesco and Sainsbury's prices do not refresh by themselves: the weekly robot only covers Aldi, Lidl and Morrisons, so after two weeks the site marks them "over 2 weeks old". A loyalty-card price is used for three weeks after its check, then dropped.

**What the check found.** My old figures were about right on average (2% high) but often wrong for a single product: 99 of the 200 were out by more than 20%, and 28 by more than 40% (gravy granules £1.25 against a real 45p, quinoa £1.75 against £3.10).

**How the estimates work now.** Any price without a green tag is an estimate, and the site says "Estimate" where it used to say "Sample price". Each product's starting price is the middle of the real prices found at the three shops (or my own figure, corrected by aisle, where none was found). Each shop then gets its usual price level against that, taken from Which?'s July 2026 comparison of a 93-item basket (Aldi £158.05, Lidl £160.70, Asda £185.81, Tesco and Morrisons £195.63, Sainsbury's £197.85 without loyalty cards, Waitrose £226.95): Aldi 0.88, Lidl 0.89, ASDA 0.96, Tesco and Morrisons 1.00, Sainsbury's 1.01, M&S 1.12 (my figure, M&S is not in that comparison), Waitrose 1.16. Aldi and Lidl are set closer than the basket says, because the basket compares brands at the big shops with own-label there. Where two or more of the three shops charge exactly the same for a pack (123 products, the price-matched staples such as butter at £1.85), ASDA, Aldi, Lidl and Iceland are given that same price. The random spread between shops was cut from 11% either way to 4%, and every shop is now taken to stock every pack size instead of a random two-thirds of them. Loose fruit and veg are sold by the kilo online, so one loose onion is still an estimate even where the bag has a real price.

**18 recipe ingredients have no real price yet**, mostly because the pack size in the product list is not one the shops sell in own-label (stock cubes come in 10s and 12s, not 8s; cornflour in 500g, not 250g) or because the item is sold by weight with no count shown (courgettes, leeks, hash browns). The 305 products that are not in any recipe were not looked up at all.

**The weekly robot covers Aldi, Lidl and Morrisons only.** ASDA, Aldi, Lidl, Waitrose, Iceland and M&S show estimates until the robot has run (M&S, Waitrose, ASDA and Iceland always, apart from a few prices checked by hand earlier). Mixing checked prices and estimates can make an estimated shop look cheaper than it really is, so read the green "live" tags. Adding the other shops needs extra paid keys, and I can add them later.

**Sales.** Aldi's and Lidl's results include a "was" price when something is discounted, so sales show up with an end date one week later (they switch off by themselves). Morrisons doesn't give a "was" price, so Morrisons sales are not detected. The Morrisons price you see is whatever it lists that day.

**Aldi prices are in-store reference prices.** Aldi's website shows prices but you can't order groceries from it, so these are the shelf prices it lists.

**These are other people's scrapers.** The three Apify tools are community-made and can break when a shop redesigns its site. When that happens you'll see it in the report ("Used this run? NO") and the old prices simply stay. Also, shops' terms generally discourage automated collection of their prices. This is a small personal project, but it's your call, and if a shop ever objects, tell me and I'll take it out of the robot.

**Not every ingredient will match in every shop.** Stock cubes are skipped entirely for now (the catalogue says 8 per pack, real packs hold 10 or 12). Some things a shop simply doesn't sell, or sells only in organic or flavoured versions. Those keep whatever price they had, or stay as estimates.

**Prices not refreshed for 6 weeks are removed** (if the shop was searched successfully but no longer lists a matching product), so a stale price doesn't hang around looking current.

## Privacy, security and standards

The site was checked against four common "before you launch" checklists. This is what it has, what was left out on purpose, and the two things only you can do.

**What the site has**

- **Privacy page and Terms of use page**, linked from the bottom of every page, in plain English. The Terms page also covers what a refund policy would (the site is free, so there is nothing to refund).
- **No collection of personal information.** No accounts, no forms that send anything, no cookies, no adverts, no analytics. Choices are saved in the visitor's own browser only (shops, My shop, shopping list, leftovers, own recipes and what was written for them, changes saved to recipes, the kitchen ticks, the fitness goal, the weekly budget, the monthly savings totals, favourites, the meal planner and the history of meals and shops), and the postcode is not saved anywhere. The Privacy page lists what is saved right now and has a **Delete everything saved** button.
- **Nothing loaded from other companies.** The font (Archivo) is built into the page, where earlier versions fetched it from Google Fonts on every visit. The only requests the site makes are to itself.
- **A security policy in the page** (a Content-Security-Policy). It lists the two exact scripts the page may run and blocks everything else: injected scripts, outside images, frames, and forms that post to other sites. Outgoing links do not tell the other site where the visitor came from.
- **HTTPS.** Visits over plain `http://` are moved to `https://` (step 6 also ticks GitHub's own setting).
- **No secrets in the page.** The Apify token lives only in GitHub's secret store (step 9). It is never in `index.html`, `prices.json` or any file a visitor can read.
- **Search and sharing:** a page title and description, a link-preview picture, an icon, `robots.txt`, a sitemap, and a custom "page not found" page.
- **Accessibility:** every page passes an automated accessibility check (WCAG 2.1 AA rules, including colour contrast) in light and dark mode, on desktop and phone widths. There is a "Skip to the main content" link, every drawing has a text description, everything works by keyboard, nothing scrolls sideways on a phone, and each page has its own title in the browser tab.
- **Phones.** The site is laid out for phones as well as computers: a shorter header, recipe cards two to a row, the dish picture straight under the recipe title, buttons big enough to tap (at least 40px), text boxes that do not make an iPhone zoom in, and a "Swipe sideways" note above the one wide price table. Checked on five phone sizes (320 to 414 pixels wide), upright and sideways, in light and dark mode. The phone rules only apply to narrow screens: the computer layout was compared picture by picture before and after and is identical.
- **A logo that goes home.** A small Plateful logo sits at the top of every page except the home page and goes back to the recipes.
- **Honest wording.** Estimated prices are labelled as estimates everywhere, including in the search-engine description. The site says it is independent of the supermarkets. Fonts and data are credited at the bottom of the page with their licences.

**Left out on purpose**

- **Cookie consent banner.** A banner asks permission for cookies or tracking that are not strictly needed. Plateful has none, so there is nothing to ask permission for. The footer says so in one line and the Privacy page explains it. If you ever add analytics or adverts, a banner becomes necessary: tell me first.
- **Analytics.** Adding visitor counting would mean collecting information about visitors, which goes against the "collects nothing" promise. If you want numbers later, there are privacy-friendly counters that use no cookies. Ask me and I'll explain the choices.
- **Spam protection, unsubscribe links, age checks, refund policy.** These apply to sites with contact forms, mailing lists, children's accounts or payments. Plateful has none of them.
- **Phone number and email links.** You chose not to show contact details yet.

**Only you can do these**

1. Tick **Enforce HTTPS** (step 6).
2. Decide whether to show a contact email (see "Changing things later").

**One honest limit.** The Privacy and Terms pages are written carefully in plain English, but I am not a lawyer and they are not legal advice. For a personal project that collects nothing they are a sensible starting point. If Plateful ever takes payments, holds accounts or becomes a business, have them checked.

## Changing things later

- **New version of the site.** When I give you a new `index.html`, upload it over the old one (**Add file**, **Upload files**), together with the new `404.html`. Don't touch `prices.json`: it holds the latest prices. The link-preview address is filled in again by itself at the next Monday run, or straight away if you run the workflow in **test** mode.
- **Don't edit `index.html` or `404.html` by hand.** Each one lists the exact scripts it is allowed to run (see "Privacy, security and standards" below). If a script inside is changed by even one character, the browser refuses to run it and the page goes blank. Ask me for the change instead and I'll give you a new file.
- **Adding a contact email.** The Privacy page says who runs the site but shows no email, because you chose not to show one yet. Tell me the address when you have one and I'll add it to the Privacy page and the footer.
- **Adding an ingredient to the site.** It also needs an entry in `pipeline/config.json`. The price job checks this first and stops with a clear message if one is missing. The same check also stops the run if a matching rule has a stray `|` in it (that would make it reject every product).
- **Changing how something is matched.** Each ingredient in `pipeline/config.json` has a search word (`kw`), words that must appear (`must`), words that rule a product out (`avoid`), an optional preference (`prefer`), and more. Ask me and I'll edit it.
- **Offline tests.** `python pipeline/tests/run_tests.py` checks the matching rules with made-up data. No internet or money needed.
- **Estimate the cost of a run.** `python pipeline/update_prices.py --mode live --estimate` prints the cost of a full run, of this week's due ingredients, and the average week and month. Add `--shops aldi,lidl` to see a cheaper set of shops.

## The files

| File | What it is |
|---|---|
| `index.html` | The website. |
| `404.html` | The "Nothing on this plate" page shown for a wrong address. |
| `robots.txt` | Tells search engines they may read the site, and where the sitemap is. |
| `sitemap.xml` | The list of pages for search engines. The robot creates it on its first run (step 10). |
| `favicon.svg`, `apple-touch-icon.png` | The plate icon for browser tabs and phone home screens. |
| `og-image.png` | The picture shown when the site's link is shared in a message. |
| `licences/Archivo-font-OFL.txt` | The licence of the Archivo font, which is built into the pages. It has to travel with the font. |
| `pipeline/site_address.py` | Works out the site's web address and writes it into the files above. The robot runs it. |
| `prices.json` | The current live prices. The robot rewrites this every run. |
| `pipeline/update_prices.py` | The price-fetching script. |
| `pipeline/config.json` | How each ingredient is searched for and recognised. |
| `pipeline/last-run-report.md` | What the last run picked and rejected. Rewritten every run. |
| `pipeline/samples/` | Raw shop output saved by test runs, for tuning. |
| `pipeline/tests/run_tests.py` | Offline tests. |
| `github-workflow/update-prices.yml` | A copy of the robot's instructions. The working copy lives at `.github/workflows/update-prices.yml` (step 4). |
| `pipeline/browser_search.py` | The part of the home price checker that reads prices from the shop pages in a browser. |
| `price-checker/check_prices.py` | The home price checker (see "Home price checker"). |
| `price-checker/settings.json` | Your repository name, which shops, and how often. |
| `price-checker/*.command`, `*.bat` | Double-click helpers: setup, trial, run now, schedule, unschedule (Mac and Windows). |
