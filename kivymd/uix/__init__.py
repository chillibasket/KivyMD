__all__ = ("MDAdaptiveWidget",)

from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class MDAdaptiveWidget:
    adaptive_height = BooleanProperty(False)
    """
    If `True`, the following properties will be applied to the widget:

    .. code-block:: kv

        size_hint_y: None
        height: self.minimum_height

    :attr:`adaptive_height` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    adaptive_width = BooleanProperty(False)
    """
    If `True`, the following properties will be applied to the widget:

    .. code-block:: kv

        size_hint_x: None
        width: self.minimum_width

    :attr:`adaptive_width` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    adaptive_size = BooleanProperty(False)
    """
    If `True`, the following properties will be applied to the widget:

    .. code-block:: kv

        size_hint: None, None
        size: self.minimum_size

    :attr:`adaptive_size` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    def _set_adaptive_binding(self, name: str, follows: str, callback) -> None:
        """Give an adaptive property a single binding.

        :param name: the adaptive property the binding belongs to
        :param follows: the property whose changes are followed
        :param callback: handler to bind, or `None` to only remove the
                         binding which is currently in place
        """

        bindings = self.__dict__.setdefault("_adaptive_bindings", {})
        current = bindings.pop(name, None)

        if current is not None:
            self.unbind(**{current[0]: current[1]})

        if callback is not None:
            self.bind(**{follows: callback})
            bindings[name] = (follows, callback)

    def _adaptive_texture_height(self, *args) -> None:
        if self.height != self.texture_size[1]:
            self.height = self.texture_size[1]

    def _adaptive_texture_width(self, *args) -> None:
        if self.width != self.texture_size[0]:
            self.width = self.texture_size[0]

    def _adaptive_texture_size(self, *args) -> None:
        if tuple(self.size) != tuple(self.texture_size):
            self.size = self.texture_size

    def _adaptive_minimum_height(self, *args) -> None:
        if self.height != self.minimum_height:
            self.height = self.minimum_height

    def _adaptive_minimum_width(self, *args) -> None:
        if self.width != self.minimum_width:
            self.width = self.minimum_width

    def _adaptive_minimum_size(self, *args) -> None:
        if tuple(self.size) != tuple(self.minimum_size):
            self.size = self.minimum_size

    def on_adaptive_height(self, md_widget, value: bool) -> None:
        if value:
            self.size_hint_y = None

        if issubclass(self.__class__, Label):
            self._set_adaptive_binding(
                "adaptive_height",
                "texture_size",
                self._adaptive_texture_height if value else None,
            )
            if value:
                self._adaptive_texture_height()
        elif not isinstance(self, (FloatLayout, Screen)):
            self._set_adaptive_binding(
                "adaptive_height",
                "minimum_height",
                self._adaptive_minimum_height if value else None,
            )
            if value and not self.children:
                self.height = 0

    def on_adaptive_width(self, md_widget, value: bool) -> None:
        if value:
            self.size_hint_x = None

        if issubclass(self.__class__, Label):
            self._set_adaptive_binding(
                "adaptive_width",
                "texture_size",
                self._adaptive_texture_width if value else None,
            )
            if value:
                self._adaptive_texture_width()
        elif not isinstance(self, (FloatLayout, Screen)):
            self._set_adaptive_binding(
                "adaptive_width",
                "minimum_width",
                self._adaptive_minimum_width if value else None,
            )
            if value and not self.children:
                self.width = 0

    def on_adaptive_size(self, md_widget, value: bool) -> None:
        if value:
            self.size_hint = (None, None)

        if issubclass(self.__class__, Label):
            if value:
                self.text_size = (None, None)
            self._set_adaptive_binding(
                "adaptive_size",
                "texture_size",
                self._adaptive_texture_size if value else None,
            )
            if value:
                self._adaptive_texture_size()
        elif not isinstance(self, (FloatLayout, Screen)):
            self._set_adaptive_binding(
                "adaptive_size",
                "minimum_size",
                self._adaptive_minimum_size if value else None,
            )
            if value and not self.children:
                self.size = (0, 0)
