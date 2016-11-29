# pector
simple python vector/matrix lib with focus on 3d geomety

Every once and then a programmer should learn a new language and reimplement old stuff using new paradigms.
If just for the sake of fascination.

This is an attempt to write the basic building blocks for audio-visual art,
namely the functional wrappers for pythagorean manipulation of position and transformation, in a most pythonian way.

### rationale ###

In an embedded python, inside an audio-visual framework in C++, i want to give the user intuitive, simply and fast
vector/matrix/transformation-handling types to interface with the main app. All in a GLSL-like fashion.
From my point of view, there is no common, simple vector/matrix lib for python except numpy,
which i do not want to depend on, and which does not handle vec3 and vec4 any special.
There are numerous little libs like this one, though. Be recreating the wheel,
i just want to get familiar with python in general.

Once the interface is settled, i hope it's possible to compile the lib with Cython
or any other tool that creates the C/Python function wrappers,
and to replace the C function bodies with the usual super-efficient c-style matrix math wizardry
and to use inplace operations as much as possible, get rid of the internal python list object, etc..

I've started to write a C extension like this from the CPython side which was an interesting task
but which is hard to sustain and doesn't teach me good python after all 
