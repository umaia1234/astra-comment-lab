import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const sharp=require('sharp');
const dir=path.dirname(fileURLToPath(import.meta.url));
const stage=3;
const defs=`<defs>
<linearGradient id="skin" x1="0" x2="1" y1=".3" y2=".7"><stop stop-color="#efc697"/><stop offset=".5" stop-color="#e4b17f"/><stop offset="1" stop-color="#bd8358"/></linearGradient>
<linearGradient id="suit" x2="1" y2="1"><stop stop-color="#34414b"/><stop offset="1" stop-color="#172631"/></linearGradient>
<linearGradient id="neck" x2=".2" y2="1"><stop stop-color="#b77b4e"/><stop offset="1" stop-color="#deb27c"/></linearGradient>
<linearGradient id="tie" x2="1" y2=".3"><stop stop-color="#b0a168"/><stop offset=".5" stop-color="#e4d6a0"/><stop offset="1" stop-color="#8c794d"/></linearGradient>
<linearGradient id="nose" x1="0" x2="1"><stop stop-color="#ebbd88"/><stop offset=".48" stop-color="#f2c695"/><stop offset="1" stop-color="#bc8156"/></linearGradient>
<radialGradient id="cheek"><stop stop-color="#f7d6a7"/><stop offset="1" stop-color="#e4b17f" stop-opacity="0"/></radialGradient>
<pattern id="silk" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(16)"><path d="m2 0 4 5-4 5-4-5Z" fill="#f6e4af" opacity=".5"/><path d="m7 0 4 5-4 5-4-5Z" fill="#74623e" opacity=".3"/></pattern>
<clipPath id="hairClip"><path d="M280 469C250 428 248 382 244 333 243 276 264 218 285 176 343 108 435 80 601 71 689 47 814 144 796 289 837 348 800 416 752 449L735 365C729 292 700 256 627 237 528 207 440 236 373 250 333 287 317 366 311 436L309 476Z"/></clipPath>
</defs>`;
const layers=[];
layers.push(`<rect width="1093" height="1381" fill="#e9e4d8"/><circle cx="550" cy="519" r="443" fill="#cbd8ce"/>`);
layers.push(`<path d="M1 1381 38 1045Q54 906 126 863L414 747 756 635 813 733 1030 810Q1093 835 1093 913V1381Z" fill="url(#suit)"/>`);
layers.push(`<path d="M404 708 741 626 759 749 633 880 498 916 418 862Z" fill="url(#neck)"/>`);
layers.push(`<path d="m421 754 74 116 205-146 54-78 5 85-153 242-44 156-137 62-26-178Z" fill="#f6f5ef"/>`);
layers.push(`<path d="m490 883 74 73-57 63 34 362H380l65-365-24-69Z" fill="url(#tie)"/>`);
layers.push(`<path d="M421 754 379 831 394 996 371 1205 307 1381H209l116-341-28-160Z" fill="#253440"/><path d="m758 646 91 134-33 120-67 30 82 80-335 371H374l232-408 144-225Z" fill="#263744"/>`);
layers.push(`<path d="M327 271C379 237 497 215 566 224 640 211 710 242 735 288L768 408C796 380 811 401 804 453L788 544Q784 578 755 638C738 705 686 751 618 774C560 802 492 790 441 764Q404 744 373 704C335 689 305 622 295 572 275 561 264 527 265 490L269 446C283 424 305 454 313 464L325 356Z" fill="url(#skin)"/>`);
layers.push(`<path d="M280 469C250 428 248 382 244 333 243 276 264 218 285 176 343 108 435 80 601 71 689 47 814 144 796 289 837 348 800 416 752 449L735 365C729 292 700 256 627 237 528 207 440 236 373 250 333 287 317 366 311 436L309 476Z" fill="#202b2d"/>`);
// New facial detail is added in subsequent actual saves while the preview is recorded.
const detail=[];
detail.push(`<path d="M292 459Q274 447 280 493L292 541 309 558 306 513 295 483Z" fill="#d19363"/><path d="M303 481Q278 456 291 519" fill="none" stroke="#b87950" stroke-width="6" stroke-linecap="round"/><path d="M765 422Q795 399 791 445L779 518 761 538 754 491Z" fill="#b97e54"/><path d="M770 437Q784 420 779 463L766 491" fill="none" stroke="#916044" stroke-width="7" stroke-linecap="round"/>`);
detail.push(`<path d="M704 295Q742 395 725 486C720 534 705 555 707 599 700 665 657 728 595 768Q715 740 755 638L771 543 763 414Q745 339 704 295Z" fill="#a66e4e" opacity=".22"/>`);
detail.push(`<ellipse cx="391" cy="518" rx="86" ry="100" fill="url(#cheek)"/><ellipse cx="635" cy="510" rx="82" ry="105" fill="url(#cheek)"/><path d="M336 434Q331 505 356 557L387 570Q352 516 361 459Z" fill="#eec697" opacity=".6"/>`);
detail.push(`<path d="M482 364C485 410 481 472 464 522Q448 552 461 573C485 589 548 585 583 575Q602 568 586 544C551 520 541 454 536 393L527 352Z" fill="url(#nose)"/>`);
detail.push(`<path d="M574 522Q600 540 605 571L589 583 565 580Q590 567 574 552Z" fill="#9c6245" opacity=".7"/><path d="M466 574Q477 569 490 575M546 577Q560 569 577 572" fill="none" stroke="#865136" stroke-width="5" stroke-linecap="round"/>`);
detail.push(`<path d="M501 424C497 468 481 524 478 548Q483 557 496 550" fill="none" stroke="#f7d6a2" stroke-width="9" stroke-linecap="round" opacity=".65"/>`);
detail.push(`<path d="M444 573C429 590 410 616 414 643Q418 665 431 676M604 577C628 596 651 617 646 647" fill="none" stroke="#ad754f" stroke-width="5" stroke-linecap="round" opacity=".5"/>`);
detail.push(`<path d="M379 645Q409 722 475 753C516 774 570 777 614 755Q549 799 478 766Q418 744 379 645Z" fill="#f0c591" opacity=".65"/>`);
detail.push(`<path d="M359 401Q377 373 411 367C433 362 452 372 464 381L462 391Q421 378 390 391Z" fill="#64503c"/><path d="M554 377C580 354 620 344 651 361Q675 374 685 391L676 397Q612 370 560 393Z" fill="#59432f"/>`);
detail.push(`<path d="M381 443C404 424 436 421 459 439L455 450Q417 459 383 449Z" fill="#f6e9d1"/><path d="M575 434C600 416 627 416 651 429L650 441Q611 452 578 443Z" fill="#f7ebd4"/>`);
detail.push(`<ellipse cx="418" cy="440" rx="18" ry="13" fill="#443a2a"/><ellipse cx="419" cy="439" rx="11" ry="13" fill="#1e2725"/><ellipse cx="615" cy="433" rx="18" ry="13" fill="#403827"/><ellipse cx="615" cy="433" rx="11" ry="12" fill="#182421"/><circle cx="412" cy="435" r="4" fill="#fcfaf2"/><circle cx="609" cy="428" r="4" fill="#fffdf1"/>`);
detail.push(`<path d="M378 445C405 421 437 422 462 441M574 436C601 413 627 415 655 433" fill="none" stroke="#69462e" stroke-width="5" stroke-linecap="round"/><path d="M377 451Q419 469 459 448M577 444Q615 459 654 440" fill="none" stroke="#c18d5c" stroke-width="4" stroke-linecap="round"/>`);
detail.push(`<path d="M428 634C469 632 488 639 516 634C543 628 562 637 585 630L623 618C611 642 590 655 548 664C505 671 458 657 428 634Z" fill="#ad7253"/><path d="M446 650C483 664 538 669 580 650Q558 687 515 690Q470 685 446 650Z" fill="#c38a62"/><path d="M428 634C469 651 515 657 559 646Q603 639 623 623" fill="none" stroke="#785039" stroke-width="5" stroke-linecap="round"/><path d="M472 672Q512 684 552 671" fill="none" stroke="#e6b17f" stroke-width="5" stroke-linecap="round"/>`);
// Likeness refinements: forehead folds, smile lines and the swept gray hair.
detail.push(`<g fill="none" stroke-linecap="round">
<path d="M369 334Q468 296 652 316" stroke="#b9895c" stroke-width="3" opacity=".52"/>
<path d="M419 287Q510 300 600 291" stroke="#f5d4a6" stroke-width="4" opacity=".7"/>
<path d="M474 349Q482 375 480 397M522 340Q526 365 530 384" stroke="#c18f60" stroke-width="4"/>
<path d="M492 349Q491 376 493 392" stroke="#f4d1a0" stroke-width="5"/>
<path d="M381 414Q420 394 455 413M572 406Q613 390 648 409" stroke="#b88054" stroke-width="3" opacity=".8"/>
<path d="M362 453 345 462M366 461 350 476M654 441 679 447M655 450 683 463" stroke="#ba8456" stroke-width="3"/>
<path d="M376 470Q416 489 457 466M579 463Q620 487 664 462" stroke="#bc8c5d" stroke-width="3.5"/>
<path d="M377 477Q417 496 452 478M584 472Q622 491 657 473" stroke="#f6d3a0" stroke-width="4" opacity=".65"/>
<path d="M404 602Q388 622 396 656M658 602Q675 630 662 658" stroke="#cf9a68" stroke-width="3"/>
<path d="M465 720Q512 740 568 718" stroke="#c99765" stroke-width="3" opacity=".5"/>
</g>`);
detail.push(`<g clip-path="url(#hairClip)" fill="none" stroke-linecap="round">`);
for(let i=0;i<25;i++){
  const y=128+i*5.3;
  detail.push(`<path d="M${256-i*1.2} ${y+164}C${327+i*3} ${y-16} ${544+i*2} ${y-91} ${614+i*.5} ${y+45}" stroke="${i%4===0?'#87908a':'#4e5b58'}" stroke-width="${i%3===0?2.6:1.7}" opacity="${i%4===0?.62:.58}"/>`);
}
for(let i=0;i<14;i++){
  detail.push(`<path d="M${683+i*3} ${179+i*6}Q${735+i*3} ${223+i*5} ${812+i} ${239+i*8}" stroke="#687773" stroke-width="1.8" opacity=".55"/>`);
}
for(let i=0;i<14;i++){
  detail.push(`<path d="M${255+i*3} ${315+i*6}Q${273+i*2} ${334+i*4} ${290+i*2} ${417+i*4}" stroke="#a6a49a" stroke-width="${i%3===0?2.6:1.6}" opacity=".58"/>`);
}
detail.push('</g>');
detail.push(`<path d="m490 883 74 73-57 63 34 362H380l65-365-24-69Z" fill="url(#silk)"/>`);
detail.push(`<g fill="none" stroke="#5c6a73" stroke-width="2" opacity=".5"><path d="m416 769-105 114 39 50-15 115-83 320M765 669l67 113-31 105-69 37 82 85-304 346"/><path d="m325 1040 69-44M749 930l67-30"/></g>`);
for(let i=0;i<10;i++){
  detail.push(`<path d="M${88+i*18} ${935-i*4}Q${105+i*18} 1060 ${51+i*19} 1368" fill="none" stroke="#7c878b" stroke-width="1.4" opacity=".2"/>`);
}
for(let i=0;i<10;i++){
  detail.push(`<path d="M${899+i*19} ${837+i*7}  ${850+i*20} 1368" fill="none" stroke="#7c878b" stroke-width="1.4" opacity=".18"/>`);
}
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1093" height="1381" viewBox="0 0 1093 1381"><title>노무현 전 대통령 — SVG 초상화</title><desc>Codex로 SVG 경로를 직접 구성한 스타일화 초상화. 참고 사진: 대한민국 국가기록원, Roh Moo-hyun presidential portrait, Wikimedia Commons, KOGL Type 1.</desc>${defs}${layers.join('')}${detail.join('')}</svg>`;
await fs.mkdir(dir,{recursive:true});
await fs.writeFile(path.join(dir,'portrait.svg'),svg);
await fs.writeFile(path.join(dir,`portrait-stage-${stage}.svg`),svg);
await sharp(Buffer.from(svg)).resize({height:700}).png().toFile(path.join(dir,'preview-next.png'));
await fs.rename(path.join(dir,'preview-next.png'),path.join(dir,'preview.png'));
await fs.appendFile(path.join(dir,'portrait-build-log.jsonl'),JSON.stringify({time:new Date().toISOString(),stage,paths:(svg.match(/<path\b/g)||[]).length,bytes:Buffer.byteLength(svg)})+'\n');
console.log(JSON.stringify({stage,paths:(svg.match(/<path\b/g)||[]).length,bytes:Buffer.byteLength(svg)}));
