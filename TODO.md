
# IMPORTANT
* Burn in nodes at creation. Reinit reads from this attribute
* Get guide.remove() working correctly. This means strict guide and connector reinit()

## Stretch goal
* Create a name class that is much more easier and shorthand to work with

## Guide model
* ~~Get axis swap working with 4x geometry setup~~
* ~~Write more docstrings~~
* ~~Write reinit from string~~
* ~~Move aimConstraint to point at child aim transform, not guide~~
* ~~Create condition node graph for aimConstraint~~
* ~~Add up aim control shapes to be visible to user~~
* ~~Add dashed/solid hierarchical shapes~~
* ~~Add cleanup for connectors~~
* ~~Write re-init logic~~
* ~~Stress test guides parent and child logic, make sure nodes are being tidied up~~
* ~~Add custom aim targets~~
* ~~Add support for aim with X, Y or Z~~
* ~~Refactor to build on from Maya joints to allow for hierarchy and pivot movement~~
* ~~Atm guide hierarchy are properties, returning string of parent or children. Revert this back to guide objects~~
* ~~Write axis swap logic (to chang from pointing down X to Y, Z)~~
* ~~Add some methods to guide view~~
* ~~Start working on Sphinx documentation~~

## Completed stretch
* ~~Rebuild connector model after messing it up so much~~

## Connector model
* Write reinit for connector class
* ~~Add NXYZ logic~~

## Core
* Write logging tool
* Figure out how to build an API for users

## IO
* Write position save/load logic
* Write hierarhcy (aim) save/load/ logic
* Write template save/load logic

## Template
* Create a template from guides

## UI
* ~~Create simple widget for guides~~
* PLAN PLAN PLAN PLAN PLAN 
* Write plugin logic

## Web
* Create web page for skeleton forge app
