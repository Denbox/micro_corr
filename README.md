# Homemade Micro Corruption

## What?

This repository is my attempt at answering the question, "Can I use my own CPU and CLI to play [Micro Corruption](https://microcorruption.com/)?"

Micro Corruption is a fantastic mini-CTF / training series introducing players to embedded systems reverse engineering. If these words are new to you, just think "intro to Internet of Things hacking."

It often deals with concepts that most programmers don't have to consider in their day to day... like how does the code get executed on my machine and what inherent flaws in our computing systems can be exploited with a single box to enter a password in? (spoiler alert: a lot more ways than you'd think!)

If this is what you're interested in, please head over to microcorruption and jump in! While I said "intro to IoT hacking", just remember that hacking takes a lot of computer knowledge, and you might get stuck. I tried to start a few years ago and basically made no progress - it is only on recent attempts that I can get past the first few levels or so.

However, there are other, perhaps unintended interesting questions that microcorruption brings to the table! There's a CPU we are exploiting? Where is it? A virtual CPU you say? So you can emulate one of these in software? What if I want to find passwords through a different set of strategies with things like SAT solvers and formal methods? How can I interop with the CTF when it wasn't designed for this?

This repository won't go all the way there, but it will lay the groundwork to answer these questions.

## Why?

There's a lot to unpack here, and that's why I've written this repo in a more narrative style. With computer hacking, there's just no getting around it - you need to learn a mountain of obscure details about how computers work. This can often be deeply frustrating and unsatisfying because those details don't need to be things like "how does this C2 framework work?", "what button did they assign this ghidra command to again?", "what's the WinDBG equivalent in gdb?"

As a mathematician, I want to make sure the frustrating details are interesting, and provide more knowledge about computers and computation - not about frameworks. I want to start with a small, simple example to build up my knowledge about CPUs, reverse engineering, and vulnerability research. In this project, I want the following things.

1. To build a simple CPU and understand what it does
2. To verify that my CPU is correct by having a ground truth
3. To build a disassembler and debugger to analyze programs statically and dynamically, and leave space to add in and develop my own tools.
4. Interop with microcorruption's web site to be able to play without my browser!

I decided to share my progress because I think many of these topics are of interest to technical people, but lots of hacking essays / projects seem like magic. I can't say for sure that this writeup will be *easy* to follow, but I do hope it pulls back the veil on some of this stuff, and that I can learn how to do it myself!

## How?

The meat of this project will be building a CPU, disassembler, and debugger. However, it is important to interoperate with the Micro Corruption site to check our work. At the end of the day, our CPU implementation must *almost exactly match* theirs for this to work!

So let's start by investigating the site.

### Website Interop
--
#### Scripting the Website?
First, we have to see whether this is even possible. Try opening up Micro Corruption in a browser, and navigate the site while watching the network tab. (on Chrome: right click site and select inspect. Then click "Network" in the tabs along the top.)

Inside of a challenge, you'll notice that there are plenty of GET and POST requests called things like "whoami", "get\_manual", "load", "snapshot?x=...", "is\_alive", etc.

You'll also notice requests being sent and received on log-in.

These are all good signs, as we can send/receive HTTP requests with other languages, and it doesn't seem like we need to run javascript for log in or challenge access.

#### CPU API
Okay, so assuming we can get to the challenges with scripts, what do we have to do to play / pass levels?

When playing Micro Corruption without scripts, we use the debugger to figure out the password, and enter the password. We can build a CPU, but it won't work without being able to load the firmware from the microcorruption site, or without the ability to submit a password.

My original fear was that the CPU would be run in locally with javascript. However, it seems that the CPU is hosted on Micro Corruption's infrastructure - meaning that the site needs some way to receive and send data to the CPU.

To answer this, we can inspect the script prefixed with "pagebody-", loaded when you enter a challenge. Looking at all of the `cpu.send` and `cpu.get` function calls, we can see that the documented CPU HTTP commands (that we have access to) are the following.

##### POST (`cpu.send`):
- `/cpu/send_input`
- `/cpu/reset`
- `/cpu/dbg/step_out`
- `/cpu/dbg/step_over`
- `/cpu/dbg/stepn`
- `/cpu/step`
- `/cpu/dbg/continue`
- `/cpu/dbg/event`
- `/cpu/regs`
- `/cpu/updatememory`
- `/cpu/is_alive`
- `/cpu/load`

##### GET (`cpu.get`):
- `/cpu/dbg/memory`
- `/cpu/snapshot`
- `/cpu/dbg/events`
- `/cpu/dbg/stepcount`
- `/cpu/dbg/memory`
- `/cpu/output`
- `/get_manual`

We probably won't implement all of these, but this is great! It seems like we'll be able to interop our own implementation of a CPU to solve challenges and request new ones. The work flow could look like this.

1. Open a challenge with our scripts using proper GET and POST requests, and download the firmware.
2. Do the challenge with our own CPU, get the password.
3. Use scripts to open up the challenge, submit proper GET and POST requests, unlock the next challenge.
4. Repeat!


#### Authentication
However, before doing all of this, we need to make sure that it's possible to access the site. I started by trying to use the requests package in python. I was hoping that something simple like the following would work.

```
# this script starts with user / pass information
# and it (tries to) end at level select

import requests

url = 'https://microcorruption.com'
user = 'username_goes_here'
password = 'password_goes_here'

with requests.Session() as s:
	response = session.get(url + '/login')
	form_data = {
	    'name': user,
	    'password': password
	}
	
	response = s.post(url + '/login', data=form_data)
```

Unfortunately, it wasn't quite this simple. The site protects against cross site scripting with a particular token that we have to pass alongside our request. The corrected code (at time of writing on 2/4/22) looks like this. If you're just getting started web scraping, this can often be frustrating, because the site fails login silently.

```
# this script starts with user / pass information
# and it ends at level select

import requests
from bs4 import BeautifulSoup

url = 'https://microcorruption.com'
user = 'username_goes_here'
password = 'password_goes_here'

with requests.Session() as s:
	response = session.get(url + '/login')
	soup = BeautifulSoup(response.text, 'html.parser')
	csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})['content']
	form_data = {
	    'name': user,
	    'password': password,
	    'authenticity_token': csrf_token
	}
	
	response = s.post(url + '/login', data=form_data)
```

You could have gotten around this required understanding of HTTP by using a tool like [playwright](https://playwright.dev/python/), but there is no need for us to run an entire browser because we don't need to execute javascript.

#### Level Select
Picking the level doesn't involve any concepts not covered in the Authentication and CPU API sections, read the code if you'd like more details.

### CPU Emulation
--

### Disassembly
--

### Debugging
--

### Tooling
--