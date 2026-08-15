# CHAPÉU&CANETA - gerador de peças de conteúdo
# uso: python3 gerar_pecas.py   (roda a partir da raiz, com o repo clonado em ./chapeuecaneta)
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cairosvg, io, os, json

W,H = 1080,1350
INK=(16,16,16); CREAM=(255,255,246); DOT=(244,244,240); YELLOW=(255,199,0); PAPER=(254,254,254)
DOTDARK=(30,30,30)
REPO='chapeuecaneta'
MOCK=f'{REPO}/assets/mockups/resenha/'
FONT=f'{REPO}/assets/fonts/Boldonse-Regular.ttf'
TRACK=-0.01                      # -1%
MT,MB,ML,GAP = 70,95,90,72
SHIRT_BOX=(110,69,699,770)       # bbox da camiseta dentro do mockup 800x820

def bold(s): return ImageFont.truetype(FONT,s)
def tw(d,t,f,tr): return sum(d.textlength(c,font=f)+tr for c in t)-tr
def dtext(d,x,y,t,f,fill,tr):
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+tr
def wrap(d,t,f,tr,mw):
    o=[];c=''
    for w in t.split():
        s=(c+' '+w).strip()
        if tw(d,s,f,tr)<=mw: c=s
        else: o.append(c); c=w
    if c:o.append(c)
    return o
def fit(d,txt,mw,maxlin,start=54,floor=32):
    s=start
    while s>floor:
        f=bold(s); tr=-s*abs(TRACK)*-1 if False else -s*0.01
        L=wrap(d,txt.upper(),f,tr,mw)
        if len(L)<=maxlin: return s,L
        s-=2
    return s,L
def dots(im,color):
    d=ImageDraw.Draw(im)
    for y in range(9,H,24):
        for x in range(0,W,24): d.rectangle([x,y,x+3,y+3],fill=color)
def svg(path,w,color=None):
    p=cairosvg.svg2png(url=path,output_width=w); im=Image.open(io.BytesIO(p)).convert('RGBA')
    if color:
        s=Image.new('RGBA',im.size,color+(255,)); s.putalpha(im.split()[3]); return s
    return im

def card_produto(est,cor,copy=None):
    m=Image.open(MOCK+f'{est}-{cor}.webp').convert('RGB')
    bg=tuple(int(v) for v in np.median(np.array(m)[0:6].reshape(-1,3),axis=0))
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im)
    x0,y0,x1,y1=SHIRT_BOX; s=m.crop((x0,y0,x1,y1))
    lines=[]; size=54
    if copy:
        size,lines=fit(d,copy,W-2*ML-20,2)
    lh=int(size*1.68); bloco=len(lines)*lh
    disp=H-MT-MB-(bloco+GAP if lines else 0)
    sw=min(int(disp*s.width/s.height), 900); sh=int(sw*s.height/s.width)
    ty=MT+(disp-sh)//2
    im.paste(s.resize((sw,sh),Image.LANCZOS),(W//2-sw//2,ty))
    if lines:
        f=bold(size); tr=-size*0.01; y=ty+sh+GAP
        for ln in lines: dtext(d,(W-tw(d,ln,f,tr))/2,y,ln,f,INK,tr); y+=lh
    return im

def card_texto(titulo,sub=None,cta=None,base='preta'):
    bg,fg = (INK,PAPER) if base=='preta' else (CREAM,INK)
    im=Image.new('RGB',(W,H),bg); dots(im, DOTDARK if base=='preta' else DOT)
    d=ImageDraw.Draw(im); y=150
    for ln,s in titulo:
        f=bold(s); tr=-s*0.01
        dtext(d,ML,y,ln.upper(),f,YELLOW if base=='preta' else INK,tr); y+=int(s*1.30)
    if sub:
        y+=44; s,L=fit(d,sub,W-2*ML,3,start=54)
        f=bold(s); tr=-s*0.01
        for ln in L: dtext(d,ML,y,ln,f,fg,tr); y+=int(s*1.5)
    if cta:
        s=40; f=bold(s); tr=-s*0.01; y=H-MB-int(s*1.5*len(cta))
        for ln in cta: dtext(d,ML,y,ln.upper(),f,YELLOW if base=='preta' else INK,tr); y+=int(s*1.5)
    badge=svg(f'{REPO}/assets/logo/stamp_outline.svg',110, PAPER if base=='preta' else INK)
    im.paste(badge,(W-ML-badge.width,150-badge.height//2),badge)
    return im

DEZ=[("fominha","preta","Pede a bola até quando não tá em campo."),
     ("craque","preta","Tem dia que você comanda o jogo."),
     ("camisa10","cinza","Não corre, não marca. Mas resolve."),
     ("zagueirao","preta","A bola pode passar. O atacante, não."),
     ("artilheiro","verde","Some o jogo todo e sai com dois."),
     ("falso9","amarela","Ninguém sabe quem marca. Nem ele."),
     ("falso10","vermelha","Assumiu a dez no grito."),
     ("falsobom","rosa","Aquece melhor do que joga."),
     ("10efaixa","branca","Camisa dez e faixa. Ninguém votou."),
     ("banheira","azul","Nunca mais voltou pra marcar.")]

if __name__=='__main__':
    out='/mnt/user-data/outputs/carrossel-abertura'; os.makedirs(out,exist_ok=True)
    card_texto([("Mestres",106),("da",50),("Resenha.",106)],"Dez tipos que todo grupo de futebol tem.",["Vista o seu.","Link na bio."]).save(f'{out}/01-capa.png')
    for i,(e,c,t) in enumerate(DEZ,start=2):
        card_produto(e,c,t).save(f'{out}/{i:02d}-{e}.png')
    card_texto([("Qual deles é",86),("o seu",86),("parceiro?",86)],None,["Marca ele aqui.","Coleção completa no link da bio."]).save(f'{out}/12-fecho.png')
    print('gerado em',out)
