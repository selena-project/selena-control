Introduction
============
Here goes the text for introduction


one asterisk: *text* ---> italics

two asterisks: **text** ---> boldface

backquotes: ``text`` for code samples.

subscript: :subscript:`text`

superscript: :superscript:`text`


* This is a bulleted list.
* It has two items, the second
  item uses two lines.
  * with a nested list
  * and some subitems



1. This is a numbered list.
2. It has two items too.

|

#. This is a numbered list.
#. It has two items too.


| These lines are
| broken exactly like in
| the source file.




This is a normal text paragraph. The next paragraph is a code sample::

   It is not processed in any way, except
   that the indentation is removed.

   It can span multiple lines.

This is a normal text paragraph again.

|

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+


|

=====  =====  =======
A      B      A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======

|

**Hyperlinks**
Use `Link text <http://www.google.com/>`_ for inline web links.


**Cross-reference**
Here is the intro cross-link: :ref:`selena_intro`


Section
=======
Text here

Sub-section
-----------
Text here

Sub-sub-section
^^^^^^^^^^^^^^^
Text here

Paragraphs
""""""""""
Text here

|

**Footnotes**

Lorem ipsum [#f1]_ dolor sit amet ... [#f2]_

.. rubric:: Footnotes

.. [#f1] Text of the first footnote.
.. [#f2] Text of the second footnote.


**Citations**

Lorem ipsum [Ref2]_ dolor sit amet.

.. [Ref2] Book or article reference, URL or whatever.



**Comments**

.. This is a comment.

..
   This whole indented block
   is a comment.

   Still in the comment.


**Images**

.. image:: ./images/gnu.png
   :height: 250
   :width: 250
   :scale: 50
   :alt: alternate text
   :align: right


**Figure**

.. figure:: ./images/gnu.png
   :height: 150
   :width: 150
   :alt: alternate text

   This is the caption of the figure (a simple paragraph).

   The legend consists of all elements after the caption.  In this
   case, the legend consists of this paragraph and the following
   table:

   +---------------+-----------------------+
   | Symbol        | Meaning               |
   +===============+=======================+
   |  CCCCC        | Campground            |
   +---------------+-----------------------+
   |  LLLLL        | Lake                  |
   +---------------+-----------------------+
   |  MMMMM        | Mountain              |
   +-----------------------+---------------+


.. DANGER::
   Beware killer rabbits 1!

.. ATTENTION::
   Beware killer rabbits 2!

.. ERROR::
   Beware killer rabbits 3!

.. HINT::
   Beware killer rabbits 4!

.. TIP::
   Beware killer rabbits 5!

.. WARNING::
   Beware killer rabbits 6!

.. note:: This is a note admonition.
   This is the second line of the first paragraph.

   - The note contains all   indented body elements
     following.
   - It includes this bullet list.






Text text text text text text text text text text text text text text text text text text text text text.

Text text text text text text text text text text text text text text text text text text text text text.

Text text text text text text text text text text text text text text text text text text text text text.
