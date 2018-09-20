### food-trends
# Food Trends web application

This repository houses my final project for the Hackbright Academy curriculum.

## Overview
Food Trends is a web application that discovers popular ingredient pairings in 
the blogosphere. It is intended for food bloggers, writers, recipe developers, 
and foodies looking to tap into current food trends. Ideally, the app could 
serve as a source of inspiration. If a user has a particular food in mind, 
they can search for that food or ingredient. The app searches through blog 
post titles with that food, uses Spoonacular’s API to parse the titles, then 
builds all combinations on the back-end. Searching returns foods or 
ingredients that bloggers have paired with the original query. The app 
generates a D3.js visualization demonstrating those pairing popularities. 
Users can also look at recent search results.

The features of this application:
1) Search for specific foods/ingredients -- then show ingredients frequently 
    paired with the search term.
2) Use D3.js to create a visual showing strength of pairings with term.
3) View recent search results

For example, if you searched "burrata", you may see that it frequently occurs 
with the term "tomato".

__APIs used__  
Spoonacular Ingredient and Nutrition API  
Twingly Blog Search API