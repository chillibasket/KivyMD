"""
Behaviors/Hover
===============

.. rubric:: Changing when the mouse is on the widget and the widget is visible.

To apply hover behavior, you must create a new class that is inherited from the
widget to which you apply the behavior and from the :attr:`HoverBehavior` class.

In `KV file`:

.. code-block:: kv

    <HoverItem@MDBoxLayout+HoverBehavior>

In `python file`:

.. code-block:: python

    class HoverItem(MDBoxLayout, HoverBehavior):
        '''Custom item implementing hover behavior.'''

After creating a class, you must define two methods for it:
:attr:`HoverBehavior.on_enter` and :attr:`HoverBehavior.on_leave`, which will be automatically called
when the mouse cursor is over the widget and when the mouse cursor goes beyond
the widget.

.. note::

    :class:`~HoverBehavior` will by default check to see if the current Widget
    is visible (i.e. not covered by a modal or popup and not a part of a
    RelativeLayout, MDTab or Carousel that is not currently visible etc)
    and will only issue events if the widget is visible.

    To get the legacy behavior that the events are always triggered, you can
    set `detect_visible` on the Widget to `False`.

.. tabs::

    .. tab:: Declarative KV style

        .. code-block:: python

            from kivy.lang import Builder

            from kivymd.app import MDApp
            from kivymd.uix.behaviors import HoverBehavior
            from kivymd.uix.boxlayout import MDBoxLayout

            KV = '''
            MDScreen
                md_bg_color: self.theme_cls.backgroundColor

                MDBoxLayout:
                    id: box
                    pos_hint: {'center_x': .5, 'center_y': .5}
                    size_hint: .8, .8
                    md_bg_color: self.theme_cls.secondaryContainerColor
            '''


            class HoverItem(MDBoxLayout, HoverBehavior):
                '''Custom item implementing hover behavior.'''

                def on_enter(self, *args):
                    '''
                    The method will be called when the mouse cursor
                    is within the borders of the current widget.
                    '''

                    self.md_bg_color = "white"

                def on_leave(self, *args):
                    '''
                    The method will be called when the mouse cursor goes beyond
                    the borders of the current widget.
                    '''

                    self.md_bg_color = self.theme_cls.secondaryContainerColor


            class Example(MDApp):
                def build(self):
                    self.screen = Builder.load_string(KV)
                    for i in range(5):
                        self.screen.ids.box.add_widget(HoverItem())
                    return self.screen


            Example().run()

    .. tab:: Declarative Python style

        .. code-block:: python

            from kivymd.app import MDApp
            from kivymd.uix.behaviors import HoverBehavior
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.screen import MDScreen


            class HoverItem(MDBoxLayout, HoverBehavior):
                '''Custom item implementing hover behavior.'''

                def on_enter(self, *args):
                    '''
                    The method will be called when the mouse cursor
                    is within the borders of the current widget.
                    '''

                    self.md_bg_color = "white"

                def on_leave(self, *args):
                    '''
                    The method will be called when the mouse cursor goes beyond
                    the borders of the current widget.
                    '''

                    self.md_bg_color = self.theme_cls.secondaryContainerColor


            class Example(MDApp):
                def build(self):
                    self.screen = (
                        MDScreen(
                            MDBoxLayout(
                                id="box",
                                pos_hint={'center_x': .5, 'center_y': .5},
                                size_hint=(.8, .8),
                                md_bg_color=self.theme_cls.secondaryContainerColor,
                            ),
                            md_bg_color=self.theme_cls.backgroundColor,
                        )
                    )
                    for i in range(5):
                        self.screen.get_ids().box.add_widget(HoverItem())
                    return self.screen


            Example().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/hover-behavior.gif
   :align: center
"""

__all__ = ("HoverBehavior",)

from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.widget import Widget


class HoverBehavior:
    """
    :Events:
        :attr:`on_enter`
            Fired when mouse enters the bbox of the widget and the widget is
            visible.
        :attr:`on_leave`
            Fired when the mouse exits the widget and the widget is visible.
    """

    hovering = BooleanProperty(False)
    """
    `True`, if the mouse cursor is within the borders of the widget.

    Note that this is set and cleared even if the widget is not visible.

    :attr:`hover` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    hover_visible = BooleanProperty(False)
    """
    `True` if hovering is `True` and is the current widget is visible.

    :attr:`hover_visible` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    enter_point = ObjectProperty(allownone=True)
    """
    Holds the last position where the mouse pointer crossed into the Widget
    if the Widget is visible and is currently in a hovering state.

    :attr:`enter_point` is a :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    detect_visible = BooleanProperty(True, deprecated=True)
    """
    Should this widget perform the visibility check?

    .. deprecated:: 2.0.0
        Use :attr:`allow_hover` instead.

    :attr:`detect_visible` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to  `True`.
    """

    allow_hover = BooleanProperty(True)
    """
    Whether to use hover behavior.

    .. versionadded:: 2.0.0

    :attr:`allow_hover` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to  `True`.
    """

    always_detect_hover = BooleanProperty(False)
    """
    Follow the pointer even when nothing about this widget appears to react
    to it.

    A widget which draws no focus state and neither overrides nor binds
    `on_enter` and `on_leave` is skipped, since working out whether the
    pointer is over it costs a walk up the widget tree and the answer would go
    unused. Handlers bound after the first mouse movement cannot be seen by
    that check - set this to `True` for those.

    .. versionadded:: 2.0.0

    :attr:`always_detect_hover` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    __events__ = ("on_enter", "on_leave")

    def __init__(self, *args, **kwargs):
        self._hover_pos = None
        self._hover_handled = None

        # Bind mouse position updates globally.
        Window.bind(mouse_pos=self.on_mouse_update)
        super().__init__(*args, **kwargs)

    def _clear_hover(self) -> None:
        """Drops the hover state, telling the widget about it if it had one."""

        self.hovering = False
        self.enter_point = None

        if self.hover_visible:
            self.hover_visible = False
            self.dispatch("on_leave")

    def _hover_is_wanted(self) -> bool:
        """Whether following the pointer over this widget changes anything."""

        if self._hover_handled is None:
            cls = type(self)
            standard = (
                "HoverBehavior.on_enter",
                "HoverBehavior.on_leave",
                "StateLayerBehavior.on_enter",
                "StateLayerBehavior.on_leave",
            )
            self._hover_handled = (
                getattr(cls.on_enter, "__qualname__", "") not in standard
                or getattr(cls.on_leave, "__qualname__", "") not in standard
            )

            # Handlers bound from outside the class count as well
            for event in ("on_enter", "on_leave"):
                try:
                    if self.get_property_observers(event):
                        self._hover_handled = True
                except Exception:
                    pass

        return (
            self._hover_handled
            or self.always_detect_hover
            or bool(getattr(self, "focus_behavior", False))
        )

    def is_mouse_inside_widget(self, pos):
        """
        Check if the mouse is within the widget boundaries in window
        coordinates.
        """

        x, y = self.to_window(*self.pos)
        return x <= pos[0] <= x + self.width and y <= pos[1] <= y + self.height

    def on_detect_visible(self, instance, value):
        Logger.warning(
            "KivyMD: "
            "The `detect_visible` attribute is deprecated. "
            "Use the `allow_hover` attribute instead."
        )
        self.allow_hover = value

    def on_mouse_update(self, *args):
        """
        Main handler for mouse movement — determines whether mouse has entered
        or exited.
        """

        if not self._hover_is_wanted() or not self.allow_hover:
            return

        pos = args[1]

        # Return if mouse position hasn't changed
        if pos == self._hover_pos:
            return

        self._hover_pos = pos

        # If widget is disabled or invisible, don't fire events
        if self.disabled or not self.width or not self.height or not self.opacity:
            self._clear_hover()
            return

        # Walks the widget tree, so it comes after all the checks above
        if not self.get_root_window():
            return

        # Check if mouse is within widget.
        if not self.is_mouse_inside_widget(pos):
            # If previously hovering — fire leave event.
            self._clear_hover()
            return

        # Already hovering — nothing new to do.
        if self.hovering:
            return

        # Mouse just entered the widget area.
        self.hovering = True
        self.hover_visible = True

        # Optional: check if the widget is actually visible in hierarchy.
        if self.allow_hover:
            widget = self
            while True:
                parent = widget.parent
                if not parent:
                    break
                try:
                    # Convert parent position to window coordinates and check
                    # overlap.
                    parent_x, parent_y = parent.to_window(*parent.pos)
                    if not (
                        parent_x <= pos[0] <= parent_x + parent.width
                        and parent_y <= pos[1] <= parent_y + parent.height
                    ):
                        self.hover_visible = False
                        break
                except Exception:
                    break
                widget = parent

            # Additionally, check if widget is covered by a sibling
            # (e.g., modal).
            parent = widget.parent
            if parent:
                for child in parent.children:
                    if child == widget:
                        break
                    if isinstance(child, Widget):
                        cx, cy = child.to_window(*child.pos)
                        if (
                            cx <= pos[0] <= cx + child.width
                            and cy <= pos[1] <= cy + child.height
                        ):
                            self.hover_visible = False
                            break

        # Fire enter event if visible.
        if self.hover_visible:
            self.enter_point = pos
            self.dispatch("on_enter")

    def on_enter(self):
        """Fired when mouse enter the bbox of the widget."""

    def on_leave(self):
        """Fired when the mouse goes outside the widget border."""
