# encoding: utf-8
__author__ = 'zjhome'

from system.models import Asset

# 附件处理相关


def get_asset_url(asset=None, asset_id=''):
    """
    find asset's url path
    :param asset:  Asset 优先级高
    :param asset_id:  string, Asset.id
    :return:
    """
    if asset is not None:
        if asset.physical_asset is not None:
            # fixme : this should be replaced by oss path, not the remore url
            return asset.physical_asset.remote_url
        else:
            return ''
    elif asset_id != '':
        asset = Asset.objects.get(id__iexact=asset)
        if asset.physical_asset is not None:
            return asset.physical_asset.remote_url
        else:
            return ''
    else:
        return ''