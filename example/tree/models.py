from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey


# A base model for the tree:
@python_2_unicode_compatible
class BaseTreeNode(PolymorphicMPTTModel):
    parent = PolymorphicTreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent'))
    title = models.CharField(_("Title"), max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Tree node")
        verbose_name_plural = _("Tree nodes")


# Create 3 derived models for the tree nodes:

class CategoryNode(BaseTreeNode):
    opening_title = models.CharField(_("Opening title"), max_length=200)
    opening_image = models.ImageField(_("Opening image"), upload_to='images', blank=True, null=True)

    class Meta:
        verbose_name = _("Category node")
        verbose_name_plural = _("Category nodes")


class TextNode(BaseTreeNode):
    extra_text = models.TextField(_('Extra text'))

    # Extra settings:
    can_have_children = False

    class Meta:
        verbose_name = _("Text node")
        verbose_name_plural = _("Text nodes")


class ImageNode(BaseTreeNode):
    image = models.ImageField(_("Image"), upload_to='images')

    class Meta:
        verbose_name = _("Image node")
        verbose_name_plural = _("Image nodes")
