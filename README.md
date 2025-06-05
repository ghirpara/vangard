# Introduction

Welcome to VANGARD (Visual-novel Art & Narrative Generation Assistant for Ren'Py & DAZ), a comprehensive toolkit of command-line and GUI applications designed to streamline your visual novel development workflow between DAZ Studio and Ren'Py. The goal of this project is to provide a collection of useful scripts, tools, and utilities that allow visual novel developers to accelerate their workflow. The current thrust of the project is focused on accelerating the workflow for the development of art assets, specifically for those working with DAZ Studio. Future goals include integration of additional utilities to help developers write Ren'Py scripts in a cohesive storyboard format -- hopefully resulting in a GUI application that can allow developers to visually design Ren'Py scripts using a classic node-and-edge model, integrating tools for image picking, character design, common scripts (e.g. inventory systems, phone systems, etc). 

# Audience 

For the command-line utility portion of the product, which is what the initial releases will focus on, the primary audience are developers. It will require a little bit of experience with Python in that the tools run as Python applications. This *does not* mean that you have to know how to program. If you can use the Microsoft App Store to install Python in your system (it's free!) then you're 99% of the way there. For additional information on how to get setup to run Python, check out the PYTHON.md file. 

# What's here?

## vangard-cli

This the primary command line utility that this project will deliver. It consists of a series of commands and scripts that I've developed over the time I've worked with DAZ Studio, mainly to address frustrations or limitations on my workflow, especially in the area of automating tasks that currently take a lot of clicks and manual, repetetive work. My goal is to continually aad to this list as I come across future improvements or additions to the workflow, as well as take input and requests from the community for things that they would love to see automated or scripted. 

## vangard-image-viewer

This is a simple utility that acts as a "lightboard" for rendered images from DAZ Studio. When running, it monitors a configurable set of directories for new rendered images and adds them to a thumbnail collection, with an option to view the fullsize image by clicking on a thumbnail. See VANGUARD_IMAGE_VIEWER.md for more details. 
