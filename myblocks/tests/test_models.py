from myblocks import models
from myblocks.tests import factories
from seo.tests.factories import SeoSiteFactory
from seo.tests.setup import DirectSEOBase


class ModelsTests(DirectSEOBase):
    def test_block_bootstrap_classes(self):
        block = factories.BlockFactory(offset=5, span=3)
        block2 = factories.BlockFactory(offset=3, span=7)

        self.assertEqual(block.bootstrap_classes(),
                         'col-md-offset-5 col-md-3')
        self.assertEqual(block2.bootstrap_classes(),
                         'col-md-offset-3 col-md-7')

    def test_block_cast(self):
        models.Block.objects.all().delete()
        factories.LoginBlockFactory()
        block = models.Block.objects.get()
        self.assertIsInstance(block, models.Block)
        self.assertIsInstance(block.cast(), models.LoginBlock)

    def test_page_all_blocks(self):
        blocks = []
        [blocks.append(factories.ContentBlockFactory()) for x in range(0, 5)]

        row = factories.RowFactory()
        [models.BlockOrder.objects.create(row=row, block=block,
                                          order=block.id)
         for block in blocks]

        [blocks.append(factories.LoginBlockFactory()) for x in range(0, 5)]

        row2 = factories.RowFactory()
        [models.BlockOrder.objects.create(row=row2, block=block,
                                          order=block.id)
         for block in blocks]

        page = factories.PageFactory(sites=(SeoSiteFactory()))
        models.RowOrder.objects.create(page=page, row=row,
                                       order=row.id)
        models.RowOrder.objects.create(page=page, row=row2,
                                       order=row2.id)

        all_blocks = page.all_blocks()
        all_blocks_ids = [block.id for block in all_blocks]
        block_ids = [block.id for block in blocks]

        self.assertItemsEqual(block_ids, all_blocks_ids)