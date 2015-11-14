parts blocking:


Models are not interactive at runtime!
--------------------------------------

# Raw model builds
* parts are built with componenets
* components are where control logic lies
* parts build is {part: [control, setup]}
* set joints before creation?

# Components
Components make up parts. Not to be confused with controls

# IDEAS to rename parts:
    scaffold (thanks laura xoxooxoxxo)
    appendage
    branch


Part
    Component
        Control
            Shapes
    Component
        Control

IkFkPart
    FkComponent
        FkControl0
        FkControl1
        FkControl2
    IkComponent
        IkControl0
        IkControl1
        IkControl2

Interactive:
    parts have component definitions
    parts hook into other parts
        components can be junctioned
            translate
            rotate
            (no scale for now)

Important ideas:
* Parts register components during creation
* Components register controls in dict ('secondary', 'secondary_index') as ley
* Controls can be juntioned, exposed at part level

