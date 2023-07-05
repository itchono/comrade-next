import re
import uuid
from typing import Awaitable, Callable

from interactions import (
    ActionRow,
    BaseContext,
    Button,
    ButtonStyle,
    Client,
    ComponentCommand,
    ComponentContext,
    Message,
)


class DynamicPaginator:
    """
    Like a Paginator, but with components,
    and can dynamically add pages

    The key member is `generate_component`, which is a coroutine
    that takes in the page number and returns the components and text for that page

    """

    client: Client
    maximum_pages: int
    message: Message
    current_page: int = 1
    custom_id_root: str
    pages: dict[int, tuple[list[ActionRow], str]]
    uuid: str

    generate_page: Callable[[int], Awaitable[tuple[list[ActionRow], str]]]

    def __init__(
        self,
        client: Client,
        generate_page: Callable[[int], Awaitable[tuple[list[ActionRow], str]]],
        maximum_pages: int,
    ):
        self.client = client
        self.generate_page = generate_page
        self.maximum_pages = maximum_pages
        self.pages = {}
        self.uuid = str(uuid.uuid4())

        # Add component callback
        self.client.add_component_callback(
            ComponentCommand(
                name=f"DynPaginator:{self.uuid}",
                callback=self.on_button,
                listeners=[re.compile(f"^{self.uuid}\|(\d+)$")],
            )
        )

    async def get_page(self, page_num: int) -> tuple[list[ActionRow], str]:
        """
        Gets the components corresponding to the nth page of the paginator
        """
        if page_num > self.maximum_pages:
            raise IndexError("Page index out of range (too large)")
        elif page_num < 1:
            raise IndexError("Page index out of range (must be >=1)")

        if page_num in self.pages:
            return self.pages[page_num]
        else:
            self.pages[page_num] = await self.generate_page(page_num)
            return self.pages[page_num]

    @property
    def page_navigation(self) -> list[ActionRow]:
        """
        Selector for switching between pages;
        uses neighbouring pages as options

        Each < > contains 5 buttons

        Examples:
        If I'm on page 1 (current_page = 1)
        < **1** | 2 | 3 | 4 | (last) >

        If I'm on page 2:
        < (first) | **2** | 3 | 4 | (last) >

        If I'm on page 3:
        < (first) | 2 | **3** | 4 | (last) >

        If I'm on page 4:
        < (first) | 3 | **4** | 5 | (last) >

        If I'm on page 5:
        < (first) | 4 | **5** | 6 | (last) >
        """

        if self.maximum_pages <= 5:
            # No need to do anything fancy
            return [
                ActionRow(
                    *[
                        Button(
                            label=str(i + 1),
                            custom_id=f"{self.uuid}|{i+1}",
                            style=ButtonStyle.PRIMARY,
                            disabled=i + 1 == self.current_page,
                        )
                        for i in range(self.maximum_pages)
                    ]
                )
            ]

        else:
            # Button structure is as follows
            # < (first button) | (middle buttons) | (last button) >
            # Content of middle buttons depends on current page

            first_button = Button(
                label="1",
                custom_id=f"{self.uuid}|1",
                style=ButtonStyle.PRIMARY
                if self.current_page == 1
                else ButtonStyle.SECONDARY,
                disabled=self.current_page == 1,
            )
            last_button = Button(
                label=str(self.maximum_pages),
                custom_id=f"{self.uuid}|{self.maximum_pages}",
                style=ButtonStyle.PRIMARY
                if self.current_page == self.maximum_pages
                else ButtonStyle.SECONDARY,
                disabled=self.current_page == self.maximum_pages,
            )

            def generate_middle_buttons(offset: int):
                return [
                    Button(
                        label=str(self.current_page + i + offset),
                        custom_id=f"{self.uuid}|{self.current_page + i + offset}",
                        style=ButtonStyle.PRIMARY,
                        disabled=self.current_page + i + offset
                        == self.current_page,
                    )
                    for i in range(3)
                ]

            offset_map = {
                2: 0,
                1: 1,
                self.maximum_pages - 1: -2,
                self.maximum_pages: -3,
            }

            offset = offset_map.get(self.current_page, -1)

            middle_buttons = generate_middle_buttons(offset)

            return [
                ActionRow(
                    *[
                        first_button,
                        *middle_buttons,
                        last_button,
                    ]
                )
            ]

    async def send(self, ctx: BaseContext) -> Message:
        """
        Send this paginator.

        Args:
            ctx: The context to send this paginator with

        Returns:
            The resulting message

        """
        page_components, content = await self.get_page(self.current_page)

        return await ctx.send(
            content=content, components=page_components + self.page_navigation
        )

    async def on_button(self, ctx: ComponentContext):
        """
        Handles button presses
        """
        page_number = int(ctx.custom_id.split("|")[1])

        if page_number == self.current_page:
            await ctx.send("You're already on that page!", ephemeral=True)
            return

        # Make sure we can actually get components for this page
        page_components, content = await self.get_page(page_number)

        self.current_page = page_number
        await ctx.edit_origin(
            content=content, components=page_components + self.page_navigation
        )
