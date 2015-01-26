# IMPORTANT
- [ ] Finish off docstrings
- [ ] Write renaming logic
- [ ] Remove index from create dialog

## Done
- [x] Write logging tool
- [x] Figure out how to build an API for users
- [x] Create simple widget for guides
- [x] Finish up guide scaling and up model inheriting guide scale
- [x] Fix up model
- [x] Write template save/load logic
- [x] Update connector model with colored 'up' nodes
- [x] Create a name class that is much more easier and shorthand to work with
- [x] Write position save/load logic
- [x] Write rebuild logic
- [x] Add compile
- [x] Fix all that duplicate reinit logic occuring in I/O read and rebuild
- [x] Work on hierarchy crawling logic. Both read and write to create a duplicate chain
- [x] Reinit connectors during guide operations so aim/state condition indexes are updated correctly for hierarchical changes
- [x] Get guide.remove() working correctly. This means strict guide and connector reinit()
- [x] Burn in nodes at creation. Reinit reads from this attribute
- [x] Get axis swap working with 4x geometry setup
- [x] Write more docstrings
- [x] Write reinit from string
- [x] Move aimConstraint to point at child aim transform, not guide
- [x] Create condition node graph for aimConstraint
- [x] Add up aim control shapes to be visible to user
- [x] Add dashed/solid hierarchical shapes
- [x] Add cleanup for connectors
- [x] Write re-init logic
- [x] Stress test guides parent and child logic, make sure nodes are being tidied up
- [x] Add custom aim targets
- [x] Add support for aim with X, Y or Z
- [x] Refactor to build on from Maya joints to allow for hierarchy and pivot movement
- [x] Atm guide hierarchy are properties, returning string of parent or children. Revert this back to guide objects
- [x] Write axis swap logic (to chang from pointing down X to Y, Z)
- [x] Add some methods to guide view
- [x] Start working on Sphinx documentation
- [x] Write reinit for connector class
- [x] Add NXYZ logic
- [x] Rebuild connector model after messing it up so much

## Future
- [ ] Create template logic
- [ ] Create Joint model for decompiling a joint into guide