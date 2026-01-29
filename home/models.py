from copy import deepcopy

from wagtail import blocks
from wagtail.blocks import BlockGroup
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock, ImageBlock
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel


# ============================================================================
# StreamField Blocks for Testing Meta.form_layout Feature
# ============================================================================
#
# This module contains blocks that test various aspects of the new
# Meta.form_layout feature in Wagtail 7.3:
#
# 1. SimpleReorderBlock:
#    - Basic field reordering using a list
#    - Uses ImageBlock (new in Wagtail)
#
# 2. PersonBlock:
#    - Nested BlockGroups with both children and settings
#    - Demonstrates mixin pattern (common theme fields)
#    - Required field (email) nested in settings to test error expansion
#    - Uses attrs on nested groups
#    - Uses ImageBlock
#
# 3. EmployeeBlock (extends PersonBlock):
#    - Demonstrates get_form_layout() override
#    - Programmatically extends parent's layout using deepcopy
#    - Adds new fields to existing groups and creates new groups
#
# 4. ArticleBlock:
#    - Custom form_template with nested StructBlock (ArticleContentBlock)
#    - Both parent and child have custom form_templates
#    - Both use BlockGroup with settings (no nested groups allowed with custom templates)
#    - Contains common theme fields (mixin pattern)
#
# 5. TestimonialBlock:
#    - Complex nested BlockGroups with multiple levels
#    - Extensive use of attrs on nested groups
#    - Multiple collapsed groups
#    - Nested BlockGroups in settings
#    - Uses both ImageBlock and ImageChooserBlock
#
# ============================================================================


class SimpleReorderBlock(blocks.StructBlock):
    """Test basic reordering of child blocks with ImageBlock"""

    first_name = blocks.CharBlock()
    surname = blocks.CharBlock()
    photo = ImageBlock(required=False)
    biography = blocks.RichTextBlock()

    class Meta:
        icon = "user"
        form_layout = [
            "photo",
            BlockGroup(
                children=["first_name", "surname"],
                heading="Name",
            ),
            "biography",
        ]


class PersonBlock(blocks.StructBlock):
    """Base person block demonstrating nested BlockGroups with settings and mixin pattern"""

    photo = ImageBlock(required=False)
    first_name = blocks.CharBlock()
    surname = blocks.CharBlock()
    biography = blocks.RichTextBlock()
    job_title = blocks.CharBlock(required=False)
    department = blocks.CharBlock(required=False)

    # Required field in nested settings to test error handling
    email = blocks.EmailBlock(required=True, help_text="Email address (required)")

    available = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Whether this person is available",
    )
    display_contact = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Show contact info on public profile",
    )

    # Common theme fields (mixin pattern)
    theme = blocks.ChoiceBlock(
        choices=[
            ("light", "Light"),
            ("dark", "Dark"),
            ("primary", "Primary Color"),
            ("secondary", "Secondary Color"),
        ],
        required=False,
        default="light",
        help_text="Select the color theme",
    )
    font_size = blocks.ChoiceBlock(
        choices=[
            ("small", "Small"),
            ("medium", "Medium"),
            ("large", "Large"),
        ],
        required=False,
        default="medium",
        help_text="Select the font size",
    )

    class Meta:
        icon = "user"
        form_layout = BlockGroup(
            children=[
                "photo",
                BlockGroup(
                    children=["surname", "first_name"],
                    heading="Basic info",
                    label_format="{first_name} {surname}",
                    attrs={"data-test": "name-group"},
                ),
                BlockGroup(
                    children=["biography"],
                    settings=["job_title", "department"],
                    heading="Biography & Work",
                    classname="collapsed",
                    icon="edit",
                    help_text="Add biographical information and work details",
                ),
            ],
            settings=[
                BlockGroup(
                    children=["available", "display_contact"],
                    settings=["email"],  # Required field nested in settings
                    heading="Contact & Visibility",
                    icon="view",
                    help_text="Email is required for internal communications",
                ),
                "theme",
                "font_size",
            ],
        )


class EmployeeBlock(PersonBlock):
    """Extended block demonstrating get_form_layout override"""

    role = blocks.CharBlock(help_text="Job role or position")
    start_date = blocks.DateBlock(required=False)
    employee_id = blocks.CharBlock(required=False, help_text="Employee ID number")
    active_status = blocks.BooleanBlock(
        required=False, default=True, help_text="Is this employee currently active"
    )

    def get_form_layout(self):
        # Use deepcopy to avoid modifying the parent's layout in-place
        form_layout = deepcopy(super().get_form_layout())

        # Add role to the "Basic info" group (second child, index 1)
        form_layout.children[1].children.append("role")

        # Add a new group for employment details
        form_layout.children.append(
            BlockGroup(
                children=["start_date", "employee_id"],
                heading="Employment Details",
                icon="date",
                classname="collapsed",
            )
        )

        # Add active_status to settings
        form_layout.settings.insert(0, "active_status")

        return form_layout

    class Meta:
        icon = "group"


class ArticleContentBlock(blocks.StructBlock):
    """Nested StructBlock with custom form_template - no nested BlockGroups allowed"""

    title = blocks.CharBlock()
    intro = blocks.TextBlock(required=False, help_text="Brief introduction")
    body = blocks.RichTextBlock()
    # Make sure having a `content` block doesn't cause any ID conflicts
    content = blocks.RichTextBlock()
    image = ImageChooserBlock(required=False)
    image_caption = blocks.CharBlock(required=False)

    alignment = blocks.ChoiceBlock(
        choices=[
            ("left", "Left"),
            ("center", "Center"),
            ("right", "Right"),
        ],
        required=False,
        default="left",
    )

    class Meta:
        icon = "doc-full"
        form_template = "home/block_forms/article_content.html"
        form_layout = BlockGroup(
            children=[
                "title",
                "intro",
                "image",
                "body",
                "content",
            ],
            settings=[
                "image_caption",
                "alignment",
            ],
        )


class ArticleBlock(blocks.StructBlock):
    """Parent StructBlock with custom form_template containing nested StructBlock with its own template"""

    headline = blocks.CharBlock()
    subheading = blocks.CharBlock(required=False)
    author = blocks.CharBlock(required=False)

    # Nested StructBlock that also has a custom form_template
    content = ArticleContentBlock()

    publish_date = blocks.DateBlock(required=False)
    featured = blocks.BooleanBlock(
        required=False, default=False, help_text="Feature this article on the homepage"
    )
    category = blocks.ChoiceBlock(
        choices=[
            ("news", "News"),
            ("blog", "Blog"),
            ("announcement", "Announcement"),
        ],
        required=False,
        help_text="Article category",
    )

    # Theme fields
    theme = blocks.ChoiceBlock(
        choices=[
            ("light", "Light"),
            ("dark", "Dark"),
            ("primary", "Primary Color"),
            ("secondary", "Secondary Color"),
        ],
        required=False,
        default="light",
        help_text="Select the color theme",
    )
    font_size = blocks.ChoiceBlock(
        choices=[
            ("small", "Small"),
            ("medium", "Medium"),
            ("large", "Large"),
        ],
        required=False,
        default="medium",
        help_text="Select the font size",
    )

    class Meta:
        icon = "doc-full-inverse"
        form_template = "home/block_forms/article.html"
        form_layout = BlockGroup(
            children=[
                "headline",
                "subheading",
                "author",
                "content",
                "publish_date",
            ],
            settings=[
                "featured",
                "category",
                "theme",
                "font_size",
            ],
        )


class TestimonialDetailsBlock(blocks.StructBlock):
    # Make sure having a `content` block doesn't cause any ID conflicts
    content = blocks.RichTextBlock()
    static = blocks.StaticBlock()


class TestimonialBlock(blocks.StructBlock):
    """Block demonstrating attrs and various nested configurations"""

    quote = blocks.TextBlock()
    author_name = blocks.CharBlock()
    author_title = blocks.CharBlock(required=False)
    author_photo = ImageBlock(required=False)
    company = blocks.CharBlock(required=False)
    company_logo = ImageChooserBlock(required=False)
    details = TestimonialDetailsBlock()

    rating = blocks.ChoiceBlock(
        choices=[
            ("5", "5 stars"),
            ("4", "4 stars"),
            ("3", "3 stars"),
        ],
        required=False,
        help_text="Testimonial rating",
    )
    show_rating = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Display the rating",
    )
    layout_style = blocks.ChoiceBlock(
        choices=[
            ("card", "Card"),
            ("inline", "Inline"),
            ("banner", "Banner"),
        ],
        required=False,
        default="card",
    )

    # Theme fields
    theme = blocks.ChoiceBlock(
        choices=[
            ("light", "Light"),
            ("dark", "Dark"),
            ("primary", "Primary Color"),
            ("secondary", "Secondary Color"),
        ],
        required=False,
        default="light",
        help_text="Select the color theme",
    )
    font_size = blocks.ChoiceBlock(
        choices=[
            ("small", "Small"),
            ("medium", "Medium"),
            ("large", "Large"),
        ],
        required=False,
        default="medium",
        help_text="Select the font size",
    )

    class Meta:
        icon = "openquote"
        form_layout = BlockGroup(
            children=[
                BlockGroup(
                    children=["quote"],
                    heading="Testimonial",
                    icon="openquote",
                    attrs={"data-quote-section": "true"},
                ),
                BlockGroup(
                    children=[
                        BlockGroup(
                            children=["author_name", "author_title"],
                            heading="Author Info",
                            attrs={"data-author-info": "true"},
                        ),
                        "author_photo",
                    ],
                    heading="Author",
                    icon="user",
                    attrs={"data-author-section": "true"},
                ),
                BlockGroup(
                    children=["company"],
                    settings=["company_logo"],
                    heading="Company",
                    icon="site",
                    classname="collapsed",
                ),
                "details",
            ],
            settings=[
                BlockGroup(
                    children=["rating"],
                    settings=["show_rating"],
                    heading="Rating",
                    icon="pick",
                ),
                "layout_style",
                "theme",
                "font_size",
            ],
        )


class HomePage(Page):
    test_stream = StreamField(
        [
            ("simple_reorder", SimpleReorderBlock()),
            ("person", PersonBlock()),
            ("employee", EmployeeBlock()),
            ("article", ArticleBlock()),
            ("testimonial", TestimonialBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("test_stream"),
    ]
