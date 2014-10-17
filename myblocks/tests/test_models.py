from myblocks import models
from myblocks.tests import factories
from seo.tests.setup import DirectSEOBase


class ModelsTests(DirectSEOBase):
    def test_block_bootstrap_classes(self):
        block = factories.BlockFactory(offset=5, span=3)
        block2 = factories.BlockFactory(offset=3, span=7)

        self.assertEqual(block.bootstrap_classes(),
                         'offset5 span3')
        self.assertEqual(block2.bootstrap_classes(),
                         'offset3 span7')

    def test_block_cast(self):
        factories.LoginBlockFactory()
        block = models.Block.objects.get()
        self.assertIsInstance(block, models.Block)
        self.assertIsInstance(block.cast(), models.LoginBlock)

    def test_page_all_blocks(self):
        blocks = []
        [blocks.append(factories.ContentBlockFactory()) for x in range(0, 5)]

        column = factories.ColumnFactory()
        [models.BlockOrder.objects.create(column=column, block=block,
                                          order=block.id)
         for block in blocks]

        [blocks.append(factories.LoginBlockFactory()) for x in range(0, 5)]

        column2 = factories.ColumnFactory()
        [models.BlockOrder.objects.create(column=column2, block=block,
                                          order=block.id)
         for block in blocks]

        page = factories.PageFactory()
        models.ColumnOrder.objects.create(page=page, column=column,
                                          order=column.id)
        models.ColumnOrder.objects.create(page=page, column=column2,
                                          order=column2.id)

        all_blocks = page.all_blocks()
        all_blocks_ids = [block.id for block in all_blocks]
        block_ids = [block.id for block in blocks]

        self.assertItemsEqual(block_ids, all_blocks_ids)