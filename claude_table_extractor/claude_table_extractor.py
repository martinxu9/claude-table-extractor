"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config

import base64
import io
from .claude_tool_use_utils import extract_table_as_json_from_image


from PIL import Image

EXTENSION_TO_MEDIA_TYPE = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}

FONT_FAMILY = "Inter, Roboto, -apple-system, BlinkMacSystemFont, avenir next, avenir, segoe ui, helvetica neue, helvetica, Ubuntu, noto, arial, sans-serif"


class State(rx.State):
    """The app state."""

    upload_files: list[str]

    # Whether we are currently uploading files.
    finished: bool = False

    extracted_table: list[list[str]]

    # Workaround for type annotation.
    preview_image = Image.open("./assets/favicon.ico")

    @rx.var
    def table_headers(self) -> list[str]:
        return self.extracted_table[0] if self.extracted_table else []

    @rx.var
    def table_content(self) -> list[list[str]]:
        return self.extracted_table[1:] if self.extracted_table else []

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the file upload."""

        # Expect only one upload
        file = files[0]
        upload_data = await file.read()
        self.preview_image = Image.open(io.BytesIO(upload_data))
        file_extension = (file.filename or "").split(".")[-1]
        if not file_extension or file_extension not in EXTENSION_TO_MEDIA_TYPE:
            raise TypeError(
                f"Internal error, unexpected file extension {file_extension}"
            )
        extracted_table = extract_table_as_json_from_image(
            image_data=base64.b64encode(upload_data).decode("utf-8"),
            image_media_type=EXTENSION_TO_MEDIA_TYPE[file_extension],
        )
        print(extracted_table)
        self.extracted_table = extracted_table
        return State.stop_upload

    async def stop_upload(self):
        """Stop the file upload."""
        self.finished = True
        return rx.clear_selected_files


def rendered_table() -> rx.Component:
    return rx.cond(
        State.extracted_table,
        rx.data_table(
            data=State.table_content,
            columns=State.table_headers,
        ),
    )


def result_section() -> rx.Component:
    return rx.cond(
        State.finished,
        rx.vstack(
            rx.accordion.root(
                rx.accordion.item(
                    header="Preview",  # type: ignore
                    content=rx.scroll_area(
                        rx.image(src=State.preview_image),
                        height="300px",
                    ),
                ),
                rx.accordion.item(
                    header="Result",  # type: ignore
                    content=rx.scroll_area(
                        rendered_table(),
                        height="300px",
                    ),
                ),
                collapsible=True,
                variant="outline",
                width="800px",
            ),
            align="start",
            width="800px",
            height="400px",
        ),
        rx.vstack(
            width="800px",
            height="400px",
        ),
    )


def upload() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.upload(
                rx.hstack(
                    rx.icon(
                        tag="paperclip",
                        height=20,
                        width=20,
                        margin="0.5em",
                    ),
                    rx.cond(
                        rx.selected_files,
                        rx.vstack(
                            rx.foreach(
                                rx.selected_files,
                                lambda t: rx.text(
                                    t,
                                    size="1",
                                    width="12em",
                                    class_name="overflow-auto",
                                ),
                            ),
                        ),
                        rx.text("Upload files", size="3", width="10em"),
                    ),
                    color="orange",
                    align="center",
                    spacing="2",
                    width="15em",
                    height="2.3em",
                ),
                multiple=False,
                accept={
                    "image/jpeg": [".jpg", ".jpeg"],
                    "image/png": [".png"],
                    "image/webp": [".webp"],
                },
                max_files=1,
                border="1px solid orange",
                border_radius="0.5em",
                # width="400px",
                # padding="1em",
            ),
            rx.button(
                "Submit",
                size="3",
                width="8em",
                variant="soft",
                on_click=State.handle_upload(rx.upload_files()),  # type: ignore
            ),
            rx.button(
                "Clear",
                size="3",
                width="8em",
                on_click=rx.clear_selected_files,
                variant="outline",
            ),
        ),
        padding="0.5em",
        align="center",
    )


def index() -> rx.Component:
    return rx.center(
        # rx.theme_panel(),
        # rx.vstack(
        rx.heading("Table Extractor", size="9", color="orange"),
        rx.el.em(
            "Powered by Claude Tool Use x ",
            rx.link("Reflex", href="https://github.com/reflex-dev/reflex"),
        ),
        upload(),
        result_section(),
        align="center",
        spacing="3",
        font_family=FONT_FAMILY,
        direction="column",
        height="100vh",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="orange"
    ),
)
app.add_page(index, title="Claude Table Extractor | Reflex")
