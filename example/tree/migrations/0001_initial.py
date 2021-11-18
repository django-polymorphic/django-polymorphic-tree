from django.db import models, migrations
import polymorphic_tree.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseTreeNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
            ],
            options={
                'verbose_name': 'Tree node',
                'verbose_name_plural': 'Tree nodes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryNode',
            fields=[
                ('basetreenode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tree.BaseTreeNode')),
                ('opening_title', models.CharField(max_length=200, verbose_name='Opening title')),
                ('opening_image', models.ImageField(upload_to='images', null=True, verbose_name='Opening image', blank=True)),
            ],
            options={
                'verbose_name': 'Category node',
                'verbose_name_plural': 'Category nodes',
            },
            bases=('tree.basetreenode',),
        ),
        migrations.CreateModel(
            name='ImageNode',
            fields=[
                ('basetreenode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tree.BaseTreeNode')),
                ('image', models.ImageField(upload_to='images', verbose_name='Image')),
            ],
            options={
                'verbose_name': 'Image node',
                'verbose_name_plural': 'Image nodes',
            },
            bases=('tree.basetreenode',),
        ),
        migrations.CreateModel(
            name='TextNode',
            fields=[
                ('basetreenode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tree.BaseTreeNode')),
                ('extra_text', models.TextField(verbose_name='Extra text')),
            ],
            options={
                'verbose_name': 'Text node',
                'verbose_name_plural': 'Text nodes',
            },
            bases=('tree.basetreenode',),
        ),
        migrations.AddField(
            model_name='basetreenode',
            name='parent',
            field=polymorphic_tree.models.PolymorphicTreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='tree.BaseTreeNode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basetreenode',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name=b'polymorphic_tree.basetreenode_set+', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
