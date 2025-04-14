from marshmallow import Schema, fields, validate

class RegistroSchemaInter(Schema):

    fechasoli = fields.String(required=True)
    uaUsuario= fields.String(required=True)
    areaUsuario= fields.String(required=True)
    nombreUsuario= fields.String(required=True)
    puestoUsuario= fields.String(required=True)
    ipUsuario= fields.String(required=True)
    correoUsuario= fields.String(required=True)
    direccion= fields.String(required=True)
    teleUsuario= fields.String(required=True)
    extUsuario= fields.String(required=True)
    nombreJefe= fields.String(required=True)
    puestoJefe= fields.String(required=True)

    descarga= fields.Boolean(required=True)
    comercio= fields.Boolean(required=True)
    redes= fields.Boolean(required=True)
    foros= fields.Boolean(required=True)
    whats= fields.Boolean(required=True)
    videos= fields.Boolean(required=True)
    dropbox= fields.Boolean(required=True)
    skype= fields.Boolean(required=True)
    wetransfer= fields.Boolean(required=True)
    team= fields.Boolean(required=True)
    otra= fields.Boolean(required=True)
    otra2= fields.Boolean(required=False)
    otra3= fields.Boolean(required=False)
    otra4= fields.Boolean(required=False)
    onedrive= fields.Boolean(required=True)

    urlDescarga= fields.String(required=False)
    justificaDescarga= fields.String(required=False)
    urlForos= fields.String(required=False)
    justificaForos= fields.String(required=False)
    urlComercio= fields.String(required=False)
    justificaComercio= fields.String(required=False)
    urlRedes= fields.String(required=False)
    justificaRedes= fields.String(required=False)
    urlVideos= fields.String(required=False)
    justificaVideos= fields.String(required=False)
    urlWhats= fields.String(required=False)
    justificaWhats= fields.String(required=False)
    urlDropbox= fields.String(required=False)
    justificaDropbox= fields.String(required=False)
    urlOnedrive= fields.String(required=False)
    justificaOnedrive= fields.String(required=False)
    urlSkype= fields.String(required=False)
    justificaSkype= fields.String(required=False)
    urlWetransfer= fields.String(required=False)
    justificaWetransfer= fields.String(required=False)
    urlTeam= fields.String(required=False)
    justificaTeam= fields.String(required=False)
    urlOtra= fields.String(required=False)
    justificaOtra= fields.String(required=False)
    otraC= fields.String(required=False)


    urlOtra2= fields.String(required=False)
    justificaOtra2= fields.String(required=False)
    otraC2= fields.String(required=False)
    urlOtra3= fields.String(required=False)
    justificaOtra3= fields.String(required=False)
    otraC3= fields.String(required=False)
    urlOtra4= fields.String(required=False)
    justificaOtra4= fields.String(required=False)
    otraC4= fields.String(required=False)

    ala= fields.String(required=False)
    piso= fields.String(required=False)


    
