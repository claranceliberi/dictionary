<template>
  <div>
    <Ribbon orientation="v" />
    <div class="wrap">
        <article class="guide">
        <div class="crumb"><router-link to="/">Ahabanza</router-link> › Uko wasoma</div>
        <h1>Uko wasoma inkoranyamuga</h1>
        <p class="lede">Iyi nkoranyamuga irimo amagambo 1601 y'ikoranabuhanga mu Kinyarwanda. Buri jambo rifite inshoza yaryo, n'uko ryitwa mu Cyongereza no mu Gifaransa.</p>

        <figure class="anno">
        <div class="runhead">Inkoranyamuga y'ikoranabuhanga</div>
        <div class="anno-body">
        <img class="anno-img" :src="'/images/img-116.jpeg'" alt=""><i class="pin p-img">7</i>
        <div><span class="hw">Meni yo gutangira</span><i class="pin">1</i> <span class="pr">(meni yô gutâangira)</span><i class="pin">2</i></div>
        <p class="def"><i class="pin">3</i>Igikoresho gitanga inzira igera kuri za gahunda, igenabikorwa, incapanyandiko n'ibindi.</p>
        <dl class="meta">
        <dt>HI <i class="pin">4</i></dt><dd><b>Ingingo y'ihagurutsa</b> (ingiingo y'ihâgurutsa)</dd>
        <dt>Eng <i class="pin">5</i></dt><dd><b>Start menu</b></dd>
        <dt>Fr</dt><dd><b>Menu de démarrage</b>; menu démarrer</dd>
        <dt>NK <i class="pin">6</i></dt><dd>Ikoranabuhanga rya mudasobwa</dd>
        </dl>
        </div>
        </figure>

        <ol class="parts">
        <li><h2>Ijambo ry'indatwa</h2>
        <p>Ni ijambo ry'Ikinyarwanda risobanurwa. Ryandikwa mu nyuguti zitsindagiye, kandi amagambo yose atondetse hakurikijwe inyuguti.</p>
        <p class="ex"><span>Urugero</span><b class="hwx">Meni yo gutangira</b></p></li>
        <li><h2>Imisomere</h2>
        <p>Iri mu dukubo nyuma y'ijambo. Igaragaza uko ijambo rivugwa, hakoreshejwe ibimenyetso by'amasaku nka â, ê, î na ô.</p>
        <p class="ex"><span>Urugero</span>Mikoro yambarwa <i class="mut">(mikoro yaambârwa)</i></p></li>
        <li><h2>Inshoza <abbr>SH</abbr></h2>
        <p>Ni igisobanuro kigufi cy'ijambo. Kuri uru rubuga iza ako kanya munsi y'ijambo, kuko ari cyo abenshi baba bashaka.</p>
        <p class="ex"><span>Urugero</span>Igipimo cy'ubwisubiremo bw'amajwi, bingana n'inshuro miliyoni ku isegonda. <i class="mut">— Megaheritse</i></p></li>
        <li><h2>Impuzanyito <abbr>HI</abbr></h2>
        <p>Ni irindi jambo ry'Ikinyarwanda rivuga kimwe n'ijambo ry'indatwa. Ntabwo amagambo yose agira impuzanyito.</p>
        <p class="ex"><span>Urugero</span>Mikoro — <b>Indangururamajwi</b></p></li>
        <li><h2>Icyongereza <abbr>Eng</abbr> n'Igifaransa <abbr>Fr</abbr></h2>
        <p>Ni uko ijambo ryitwa mu Cyongereza no mu Gifaransa. Iyo hari amagambo menshi, iry'ingenzi ryandikwa mu nyuguti zitsindagiye, andi akarikurikira.</p>
        <p class="ex"><span>Urugero</span><b>Lapel microphone</b>; lavalier microphone; clip mic</p></li>
        <li><h2>Igitsibo <abbr>NK</abbr></h2>
        <p>Ni ingeri y'ikoranabuhanga ijambo ribarizwamo, nka mudasobwa, murandasi cyangwa itumanaho. Kanda ku gitsibo ubone andi magambo yose akibarizwamo.</p>
        <p class="ex"><span>Urugero</span><router-link :to="categoryLink('Ikoranabuhanga ry\'amajwi')">Ikoranabuhanga ry'amajwi</router-link> <i class="mut">· amagambo 15</i></p></li>
        <li><h2>Ishusho</h2>
        <p>Amwe mu magambo aherekejwe n'ishusho iyerekana.</p></li>
        </ol>

        <h2 class="ttl" style="margin-top:48px">Urutonde rw'ibimenyetso mpine</h2>
        <table class="abbr-table">
        <tr><th>HI</th><td>Impuzanyito</td></tr>
        <tr><th>Eng</th><td>Icyongereza</td></tr>
        <tr><th>Fr</th><td>Igifaransa</td></tr>
        <tr><th>NK</th><td>Ingeri y'ikoranabuhanga / igitsibo</td></tr>
        <tr><th>SH</th><td>Inshoza / igisobanuro</td></tr>
        </table>
        <p class="src">Ibisobanuro birambuye biri mu gitabo <i>Inkoranyamuga y'Ikoranabuhanga</i> (2026), ipaji vi–vii.</p>
        </article>
    </div>
  </div>
</template>

<script>
import Ribbon from '../components/Ribbon.vue'
import { categoryLink } from '../format.js'

// Static guide to reading an entry. The examples are real entries
// (1138 Meni yo gutangira, 1143 Mikoro yambarwa, 1137 Megaheritse, 1140 Mikoro).
export default {
  name: 'GuideView',
  components: { Ribbon },
  methods: { categoryLink },
}
</script>
