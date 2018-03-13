# Flow-visualisation
Visualising flows from LEMs using leaflet-velocity


## Instructions to run the demo

An example of input is given with `velocity_field.hdr` and
`velocity_field.txt`. The former contains grid metadata (ESRI ASCII
grid format + additional entry that specifies the projection system
used), and the latter contains velocity data (two columns: for `u` and `v`
components)

Run the python script to convert the input data into a
leaflet-velocity compatible (json) format (you need to have Python 3,
Pandas and PyProj installed in your system):

```
$ python velocity2json.py velocity_field
```

Then open the file `demo/demo.html` in your browser.
