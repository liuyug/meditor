==================================
Using LaTeX syntax for mathematics
==================================

.. role:: m(math)
.. contents::

.. |latex| replace:: L\ :sup:`A`\ T\ :sub:`E`\ X


Introduction
============

This document describes a math plug-in for reStructuredText.
The html-writer will generate a combination of html and MathML.

.. warning::

   This document contains MathML.  Your browser may not be able to
   display it correctly!


ftp://ftp.ams.org/pub/tex/doc/amsmath/short-math-guide.pdf


Role and directive
==================

There is a role called ``math`` that can be used for inline
mathematical expressions: ``:math:`\psi(r) = \exp(-2r)``` will
produce :m:`\psi(r)=\exp(-2r)`.  Inside the back-tics you can write
anything you would write between dollar signs in a LaTeX ducument.

For producing displayed math (like an ``equation*`` environment in a
LaTeX document) there is a ``math`` directive.  If you write::

  .. math::

     \psi(r) = e^{-2r}

you will get:

.. math::

   \psi(r) = e^{-2r}


.. tip::

  If you put ``.. default-role:: math`` at the top of your
  document, then you can write ```x^2``` instead of the longer
  version: ``:math:`x^2```.  You can also introduce an
  abreviation like this ``.. role:: m(math)``.  That will allow
  you to write ``:m:`x^2``` or ```x^2`:m:``.


Commands and symbols
====================

The parser does not understand *all* math, but basic
everyday-math works.  If a command or a special symbol is not desribed
in this document, then it is probably not implemented.

The following tables are adapted from the first edition of
"The LaTeX Companion" (Goossens, Mittelbach, Samarin).


Accents
-------

  ============================  ========================
  :m:`\tilde{n}` ``\tilde{n}``  :m:`\hat{H}` ``\hat{H}``
  :m:`\bar{v}` ``\bar{v}``      :m:`\vec{R}` ``\vec{R}``
  ============================  ========================


Negated binary relations
------------------------

  ================================  ======================
  :m:`\not\in` ``\not\in``          :m:`\not =` ``\not =``
  :m:`\not \equiv` ``\not \equiv``
  ================================  ======================


Braces
------

  ============  ============  ============  ==============  ========================
  :m:`(` ``(``  :m:`[` ``[``  :m:`|` ``|``  :m:`\{` ``\{``  :m:`\langle` ``\langle``
  :m:`)` ``)``  :m:`]` ``]``  :m:`|` ``|``  :m:`\}` ``\}``  :m:`\rangle` ``\rangle``
  ============  ============  ============  ==============  ========================

  
LaTeX commands
--------------

  =====================  ==============================  ===============================
  command                example                         result
  =====================  ==============================  ===============================
  ``\sqrt``              ``\sqrt{x^2-1}``                :m:`\sqrt{x^2-1}`
  ``\frac``              ``\frac{1}{2}``                 :m:`\frac{1}{2}`
  ``\text``              ``k_{\text{B}}T``               :m:`k_{\text{B}}T`
  ``\left``, ``\right``  ``\left(\frac{1}{2}\right)^n``  :m:`\left(\frac{1}{2}\right)^n`
  ``\mathbf``            ``\mathbf{r}^2=x^2+y^2+z^2``    :m:`\mathbf{r}^2=x^2+y^2+z^2`
  ``\mathbb``            ``\mathbb{C}``                  :m:`\mathbb{C}`
  =====================  ==============================  ===============================


Greek letters 
-------------

  ================================  ================================  ================================  ================================
  :m:`\Delta` ``\Delta``            :m:`\Gamma` ``\Gamma``            :m:`\Lambda` ``\Lambda``          :m:`\Omega` ``\Omega`` 
  :m:`\Phi` ``\Phi``                :m:`\Pi` ``\Pi``                  :m:`\Psi` ``\Psi``                :m:`\Sigma` ``\Sigma`` 
  :m:`\Theta` ``\Theta``            :m:`\Upsilon` ``\Upsilon``        :m:`\Xi` ``\Xi``                  :m:`\alpha` ``\alpha`` 
  :m:`\beta` ``\beta``              :m:`\chi` ``\chi``                :m:`\delta` ``\delta``            :m:`\epsilon` ``\epsilon`` 
  :m:`\eta` ``\eta``                :m:`\gamma` ``\gamma``            :m:`\iota` ``\iota``              :m:`\kappa` ``\kappa`` 
  :m:`\lambda` ``\lambda``          :m:`\mu` ``\mu``                  :m:`\nu` ``\nu``                  :m:`\omega` ``\omega`` 
  :m:`\phi` ``\phi``                :m:`\pi` ``\pi``                  :m:`\psi` ``\psi``                :m:`\rho` ``\rho`` 
  :m:`\sigma` ``\sigma``            :m:`\tau` ``\tau``                :m:`\theta` ``\theta``            :m:`\upsilon` ``\upsilon`` 
  :m:`\varepsilon` ``\varepsilon``  :m:`\varkappa` ``\varkappa``      :m:`\varphi` ``\varphi``          :m:`\varpi` ``\varpi`` 
  :m:`\varrho` ``\varrho``          :m:`\varsigma` ``\varsigma``      :m:`\vartheta` ``\vartheta``      :m:`\xi` ``\xi`` 
  :m:`\zeta` ``\zeta``             
  ================================  ================================  ================================  ================================


Binary operation symbols
------------------------

  ==========================================  ==========================================  ==========================================
  :m:`\amalg` ``\amalg``                      :m:`\ast` ``\ast``                          :m:`\bigcirc` ``\bigcirc`` 
  :m:`\bigtriangledown` ``\bigtriangledown``  :m:`\bigtriangleup` ``\bigtriangleup``      :m:`\bullet` ``\bullet`` 
  :m:`\cap` ``\cap``                          :m:`\cdot` ``\cdot``                        :m:`\circ` ``\circ`` 
  :m:`\cup` ``\cup``                          :m:`\dagger` ``\dagger``                    :m:`\ddagger` ``\ddagger`` 
  :m:`\diamond` ``\diamond``                  :m:`\div` ``\div``                          :m:`\mp` ``\mp`` 
  :m:`\odot` ``\odot``                        :m:`\ominus` ``\ominus``                    :m:`\oplus` ``\oplus`` 
  :m:`\oslash` ``\oslash``                    :m:`\otimes` ``\otimes``                    :m:`\pm` ``\pm`` 
  :m:`\setminus` ``\setminus``                :m:`\sqcap` ``\sqcap``                      :m:`\sqcup` ``\sqcup`` 
  :m:`\star` ``\star``                        :m:`\times` ``\times``                      :m:`\triangleleft` ``\triangleleft`` 
  :m:`\triangleright` ``\triangleright``      :m:`\uplus` ``\uplus``                      :m:`\vee` ``\vee`` 
  :m:`\wedge` ``\wedge``                      :m:`\wr` ``\wr``                           
  ==========================================  ==========================================  ==========================================


Relation symbols
----------------

  ================================  ================================  ================================  ================================
  :m:`\Join` ``\Join``              :m:`\approx` ``\approx``          :m:`\asymp` ``\asymp``            :m:`\bowtie` ``\bowtie``
  :m:`\cong` ``\cong``              :m:`\dashv` ``\dashv``            :m:`\doteq` ``\doteq``            :m:`\equiv` ``\equiv``
  :m:`\frown` ``\frown``            :m:`\ge` ``\ge``                  :m:`\geq` ``\geq``                :m:`\gg` ``\gg``
  :m:`\in` ``\in``                  :m:`\le` ``\le``                  :m:`\leq` ``\leq``                :m:`\ll` ``\ll``
  :m:`\mid` ``\mid``                :m:`\models` ``\models``          :m:`\neq` ``\neq``                :m:`\ni` ``\ni``
  :m:`\parallel` ``\parallel``      :m:`\perp` ``\perp``              :m:`\prec` ``\prec``              :m:`\precsim` ``\precsim``
  :m:`\propto` ``\propto``          :m:`\sim` ``\sim``                :m:`\simeq` ``\simeq``            :m:`\smile` ``\smile``
  :m:`\sqsubset` ``\sqsubset``      :m:`\sqsubseteq` ``\sqsubseteq``  :m:`\sqsupset` ``\sqsupset``      :m:`\sqsupseteq` ``\sqsupseteq``
  :m:`\subset` ``\subset``          :m:`\subseteq` ``\subseteq``      :m:`\succ` ``\succ``              :m:`\succsim` ``\succsim``
  :m:`\supset` ``\supset``          :m:`\supseteq` ``\supseteq``      :m:`\vdash` ``\vdash``
  ================================  ================================  ================================  ================================


Arrow symbols
-------------
  ================================================  ================================================
  :m:`\Downarrow` ``\Downarrow``                    :m:`\Leftarrow` ``\Leftarrow`` 
  :m:`\Leftrightarrow` ``\Leftrightarrow``          :m:`\Longleftarrow` ``\Longleftarrow`` 
  :m:`\Longleftrightarrow` ``\Longleftrightarrow``  :m:`\Longrightarrow` ``\Longrightarrow`` 
  :m:`\Rightarrow` ``\Rightarrow``                  :m:`\Uparrow` ``\Uparrow`` 
  :m:`\Updownarrow` ``\Updownarrow``                :m:`\downarrow` ``\downarrow`` 
  :m:`\hookleftarrow` ``\hookleftarrow``            :m:`\hookrightarrow` ``\hookrightarrow`` 
  :m:`\leftarrow` ``\leftarrow``                    :m:`\leftharpoondown` ``\leftharpoondown`` 
  :m:`\leftharpoonup` ``\leftharpoonup``            :m:`\leftrightarrow` ``\leftrightarrow`` 
  :m:`\longleftarrow` ``\longleftarrow``            :m:`\longleftrightarrow` ``\longleftrightarrow`` 
  :m:`\longmapsto` ``\longmapsto``                  :m:`\longrightarrow` ``\longrightarrow`` 
  :m:`\mapsto` ``\mapsto``                          :m:`\nearrow` ``\nearrow`` 
  :m:`\nwarrow` ``\nwarrow``                        :m:`\rightarrow` ``\rightarrow`` 
  :m:`\rightharpoondown` ``\rightharpoondown``      :m:`\rightharpoonup` ``\rightharpoonup`` 
  :m:`\searrow` ``\searrow``                        :m:`\swarrow` ``\swarrow`` 
  :m:`\uparrow` ``\uparrow``                        :m:`\updownarrow` ``\updownarrow`` 
 
  ================================================  ================================================


Miscellaneous symbols
---------------------

  ==================================  ==================================  ==================================  ==================================
  :m:`\Im` ``\Im``                    :m:`\Re` ``\Re``                    :m:`\aleph` ``\aleph``              :m:`\angle` ``\angle`` 
  :m:`\bot` ``\bot``                  :m:`\cdots` ``\cdots``              :m:`\clubsuit` ``\clubsuit``        :m:`\ddots` ``\ddots`` 
  :m:`\diamondsuit` ``\diamondsuit``  :m:`\ell` ``\ell``                  :m:`\emptyset` ``\emptyset``        :m:`\exists` ``\exists`` 
  :m:`\flat` ``\flat``                :m:`\forall` ``\forall``            :m:`\hbar` ``\hbar``                :m:`\heartsuit` ``\heartsuit`` 
  :m:`\imath` ``\imath``              :m:`\infty` ``\infty``              :m:`\nabla` ``\nabla``              :m:`\natural` ``\natural`` 
  :m:`\neg` ``\neg``                  :m:`\partial` ``\partial``          :m:`\prime` ``\prime``              :m:`\sharp` ``\sharp`` 
  :m:`\spadesuit` ``\spadesuit``      :m:`\surd` ``\surd``                :m:`\top` ``\top``                  :m:`\vdots` ``\vdots`` 
  :m:`\wp` ``\wp``                   
  ==================================  ==================================  ==================================  ==================================


Variable-sized symbols
----------------------

  ==============================  ==============================  ==============================  ==============================  ==============================
  :m:`\bigcap` ``\bigcap``        :m:`\bigcup` ``\bigcup``        :m:`\bigodot` ``\bigodot``      :m:`\bigoplus` ``\bigoplus``    :m:`\bigotimes` ``\bigotimes`` 
  :m:`\biguplus` ``\biguplus``    :m:`\bigvee` ``\bigvee``        :m:`\bigwedge` ``\bigwedge``    :m:`\coprod` ``\coprod``        :m:`\int` ``\int`` 
  :m:`\oint` ``\oint``            :m:`\prod` ``\prod``            :m:`\sum` ``\sum``             
  ==============================  ==============================  ==============================  ==============================  ==============================

Log-like symbols
----------------

  ===============  ===============  ===============  ===============  ===============  ===============
  ``\arccos``      ``\arcsin``      ``\arctan``      ``\arg``         ``\cos``         ``\cosh`` 
  ``\cot``         ``\coth``        ``\csc``         ``\deg``         ``\det``         ``\dim`` 
  ``\exp``         ``\gcd``         ``\hom``         ``\inf``         ``\ker``         ``\lg`` 
  ``\lim``         ``\liminf``      ``\limsup``      ``\ln``          ``\log``         ``\max`` 
  ``\min``         ``\Pr``          ``\sec``         ``\sin``         ``\sinh``        ``\sup`` 
  ``\tan``         ``\tanh``        ``\injlim``      ``\varinjlim``   ``\varlimsup``   ``\projlim`` 
  ``\varliminf``   ``\varprojlim`` 
  ===============  ===============  ===============  ===============  ===============  ===============







Miscellaneous
=============

Displayed math can use ``\\`` and ``&`` for line shifts and
allignments::

  .. math::

     a & = (x + y)^2 \\
       & = x^2 + 2xy + y^2

The result is:

.. math::

   a & = (x + y)^2 \\
     & = x^2 + 2xy + y^2

The LaTeX writer will put displayed equations inside a ``split``
environment inside an ``equation*`` environment::

  \begin{equation*}
    \begin{split}
      a & = (x + y)^2 \\
        & = x^2 + 2xy + y^2
    \end{split}
  \end{equation*}

The ``matrix`` environment can also contain ``\\`` and ``&``::

  .. math::

    \left(\begin{matrix} a & b \\ c & d \end{matrix}\right)

Result:

.. math::

  \left(\begin{matrix} a & b \\ c & d \end{matrix}\right)



ToDo
====

* Math inside text: ``n - 1 \text{if $n$ is odd}``.
* Spaces ...
* Remove circular refs.
* Decimal numbers.
* ``\mathbb{ABC}`` does not work (use ``\mathbb{A}\mathbb{B}\mathbb{C}``).
