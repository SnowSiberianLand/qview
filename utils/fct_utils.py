# -*- coding: cp1251 -*-

import mod_dm as dm
import mod_cmn as cmn
import entity_utils as eu

#typedef strg mod_dm.IDataStorage
#typedef tctrl mod_dmsrv.TableControllerBase
#typedef table ctx_table.Table

#typedef gl dm.IGeoLayer

#typedef fct dm.IContact
#typedef fct_ed dm.IContact.IEditor

#typedef picks dm.IWellPicks
#typedef wp dm.wellpick


def getOwcId(strg, gl_id):
    """
    returns OWC ID for given GEOLAYER_ID
    returns Non when contact not fount
    """
    gl = eu.find_stratum(strg, gl_id)
    if gl is None:
        return None
        
    fct = getOwc(gl)
    if fct is None:
        return None

    return fct.getID()

def getGocId(strg, gl_id):
    """
    returns GOC ID for given GEOLAYER_ID
    returns Non when contact not found
    """
    gl = eu.find_stratum(strg, gl_id)
    if gl is None:
        return None
        
    fct = getGoc(gl)
    if fct is None:
        return None

    return fct.getID()

def getGwcId(strg, gl_id):
    """
    returns GWC ID for given GEOLAYER_ID
    returns Non when contact not found
    """
    gl = eu.find_stratum(strg, gl_id)
    if gl is None:
        return None
        
    fct = getGwc(gl)
    if fct is None:
        return None

    return fct.getID()

def getOwc(gl):
    """
    returns Oil-Water contact (OWC) for geolayer
    """
    vtmp = dm.vec_contact_t()
    gl.getContacts(vtmp)
    for fct in vtmp:
        if dm.cnt_owc == fct.getType():
            return fct

    return None

def getGoc(gl):
    """
    returns Gas-Oil contact (GOC) for geolayer
    """
    vtmp = dm.vec_contact_t()
    gl.getContacts(vtmp)
    for fct in vtmp:
        if dm.cnt_goc == fct.getType():
            return fct

    return None

def getGwc(gl):
    """
    returns Oil-Water contact (OWC) for geolayer
    """
    vtmp = dm.vec_contact_t()
    gl.getContacts(vtmp)
    for fct in vtmp:
        if dm.cnt_gwc == fct.getType():
            return fct

    return None

def getContact(gl, ct):
    """
    returns fluid contact for geolayer by type
    """
    vtmp = dm.vec_contact_t()
    gl.getContacts(vtmp)
    for fct in vtmp:
        if ct == fct.getType():
            return fct

    return None

def verifyContact(strg, gl, ct, fct_name=''):
    """
    finds or makes new Fluid contact for geolayer
    """

    if gl is None:
        return None

    if ct is None:
        return None

    rh = strg.getRegHelper()

    reg = rh.getContactRegistry()
    reg_ed = reg.getEditor()

    fct = getContact(gl, ct)
    if fct is None:

        nn_ctx = dm.new_node_context()
        nn_ctx.field_id = gl.getFieldID()
        nn_ctx.stratum_id = gl.getID()
    
        fct = reg_ed.addNewElement(nn_ctx)
        with dm.finder_update_blocker(fct.getDMO(), False):
            fct_ed = fct.getEditor()
            fct_ed.setLayerID(gl.getID())
            fct_ed.setType(ct)

        #print('Fluid contact created: {0}'.format(fct_name))

            if len(fct_name)==0: # имя не задано, формируем
                fct_name = gl.getName()
                if ct==dm.cnt_owc:
                    fct_name = '{0}_{1}'.format(fct_name,_('OWC'))
                elif ct==dm.cnt_goc:
                    fct_name = '{0}_{1}'.format(fct_name,_('GOC'))
                elif ct==dm.cnt_gwc:
                    fct_name = '{0}_{1}'.format(fct_name,_('GWC'))
        
                if len(fct.getName())==0: # если у контакта уже есть имя - не меняем
                    fct_ed.setName(fct_name)
            else:
                fct_ed.setName(fct_name) # меняем только если задано название
                
        rh.refresh_finders_add_obj(fct.getDMO(), dm.nt_fluidcontact)
    return fct

def verifyOwc(strg, gl, fct_name=''):
    """
    finds or makes new Oil-Water contact (OWC) for geolayer
    """
    return verifyContact(strg, gl, dm.cnt_owc, fct_name)

def verifyGoc(strg, gl, fct_name=''):
    """
    finds or makes new GOC for geolayer
    """
    return verifyContact(strg, gl, dm.cnt_goc, fct_name)

def verifyGwc(strg, gl, fct_name=''):
    """
    finds or makes new GWC for geolayer
    """
    return verifyContact(strg, gl, dm.cnt_gwc, fct_name)

class fct_bh_item:
    """
    элемент представления данных для ствола скважины по выбранной модели
    """
    
    def __init__(self, strg, bh_id):
        self.picks = dm.IWellPicks.make(strg, dm.db_caching, dm.cat_contactpicks)
        self.bh_id = bh_id
        
        tctx = cmn.progress_ctx()
        terr = cmn.err_info()
    
        fct_ids = cmn.vec_i32_t()
        b = self.picks.load_by_bh(bh_id, cmn.get_undefined_i32(), fct_ids, tctx, terr)


    def md(self, fct_id, mdl_id):
        wp = dm.wellpick()
        b = self.picks.get(self.bh_id, mdl_id, fct_id, wp)
        if b==False:
            return None
        
        return wp.md

    def tvd(self, fct_id, mdl_id):
        wp = dm.wellpick()
        b = self.picks.get(self.bh_id, mdl_id, fct_id, wp)
        if b==False:
            return None
        
        return wp.tvd

    def cx(self, fct_id, mdl_id):
        wp = dm.wellpick()
        b = self.picks.get(self.bh_id, mdl_id, fct_id, wp)
        if b==False:
            return None
        
        return wp.cx

    def cy(self, fct_id, mdl_id):
        wp = dm.wellpick()
        b = self.picks.get(self.bh_id, mdl_id, fct_id, wp)
        if b==False:
            return None
        
        return wp.cy
        
class fct_helper:
    """
    вспомогательный класс для быстрого получения отметок контактов по скважинам    
    """
    strg  = None    # IDataStorage

    bhdata = dict() # bhid to fct_bh_item

    def get_item(self, bh_id):
        """
        находит или создает элемент данных по скважине
        """
        item = self.bhdata.get( bh_id, None)

        if None==item:
            item = fct_bh_item(self.strg, bh_id)
            self.bhdata[bh_id] = item

        return item

    # MD ------------------------------------
    def getOwcMd(self, bh_id, gl_id, mdl_id):
        fct_id = getOwcId(self.strg, gl_id)
        if fct_id is None:
            return None

        item = self.get_item(bh_id)
            
        val = item.md(fct_id, mdl_id)
        return val

    def getGocMd(self, bh_id, gl_id, mdl_id):
        fct_id = getGocId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.md(fct_id, mdl_id)
        return val

    def getGwcMd(self, bh_id, gl_id, mdl_id):
        fct_id = getGwcId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.md(fct_id, mdl_id)
        return val

    # TVD ------------------------------------
    def getOwcTvd(self, bh_id, gl_id, mdl_id):        
        fct_id = getOwcId(self.strg, gl_id)
        if fct_id is None:
            return None

        item = self.get_item(bh_id)
            
        val = item.tvd(fct_id, mdl_id)
        return val

    def getGocTvd(self, bh_id, gl_id, mdl_id):
        fct_id = getGocId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.tvd(fct_id, mdl_id)
        return val

    def getGwcTvd(self, bh_id, gl_id, mdl_id):
        fct_id = getGwcId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.tvd(fct_id, mdl_id)
        return val

    # CX ------------------------------------
    def getOwcCx(self, bh_id, gl_id, mdl_id):        
        fct_id = getOwcId(self.strg, gl_id)
        if fct_id is None:
            return None

        item = self.get_item(bh_id)
            
        val = item.cx(fct_id, mdl_id)
        return val

    def getGocCx(self, bh_id, gl_id, mdl_id):
        fct_id = getGocId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.cx(fct_id, mdl_id)
        return val

    def getGwcCx(self, bh_id, gl_id, mdl_id):
        fct_id = getGwcId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.cx(fct_id, mdl_id)
        return val

    # CY ------------------------------------
    def getOwcCy(self, bh_id, gl_id, mdl_id):        
        fct_id = getOwcId(self.strg, gl_id)
        if fct_id is None:
            return None

        item = self.get_item(bh_id)
            
        val = item.cy(fct_id, mdl_id)
        return val

    def getGocCy(self, bh_id, gl_id, mdl_id):
        fct_id = getGocId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.cy(fct_id, mdl_id)
        return val

    def getGwcCy(self, bh_id, gl_id, mdl_id):
        fct_id = getGwcId(self.strg, gl_id)
        if fct_id is None:
            return None
        
        item = self.get_item(bh_id)

        val = item.cy(fct_id, mdl_id)
        return val
    
    def __init__(self, strg):
        self.strg = strg
        self.bhdata = dict()
