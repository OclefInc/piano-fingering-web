import csv
import json
import os, sys
import platform

from music21 import converter, stream
from music21.articulations import Fingering

from pianoplayer.hand import Hand
from pianoplayer.scorereader import reader, PIG2Stream


###########################################################
# Piano Player main analyse and annotate
###########################################################
# def run_analyse():
#     pass
#
#
# def analyse():
#     pass


def run_annotate(filename,
                 outputfile='output.xml',
                 n_measures=100,
                 start_measure=1,
                 depth=0,
                 rbeam=0,
                 lbeam=1,
                 quiet=False,
                 musescore=False,
                 below_beam=False,
                 with_vedo=0,
                 vedo_speed=False,
                 sound_off=False,
                 left_only=False,
                 right_only=False,
                 hand_size_XXS=False,
                 hand_size_XS=False,
                 hand_size_S=False,
                 hand_size_M=False,
                 hand_size_L=False,
                 hand_size_XL=True,
                 hand_size_XXL=False,
                 callback=None
                 ):
    class Args(object):
        pass
    args = Args()
    args.filename = filename
    args.outputfile = outputfile
    args.n_measures = n_measures
    args.start_measure = start_measure
    args.depth = depth
    args.rbeam = rbeam
    args.lbeam = lbeam
    args.quiet = quiet
    args.musescore = musescore
    args.below_beam = below_beam
    args.with_vedo = with_vedo
    args.vedo_speed = vedo_speed
    args.sound_off = sound_off
    args.left_only = left_only
    args.right_only = right_only
    args.hand_size_XXS = hand_size_XXS
    args.hand_size_XS = hand_size_XS
    args.hand_size_S = hand_size_S
    args.hand_size_M = hand_size_M
    args.hand_size_L = hand_size_L
    args.hand_size_XL = hand_size_XL
    args.hand_size_XXL = hand_size_XXL
    args.callback = callback
    annotate(args)


def annotate_fingers_xml(sf, hand, args, is_right=True):
    print('len noteseq', len(hand.noteseq))
    p0 = sf.parts[args.rbeam if is_right else args.lbeam]
    idx = 0
    total_notes = 0

    # Count total expected notes to process
    for el in p0.flat.getElementsByClass("GeneralNote"):
        if el.isNote:
            total_notes += 1
        elif el.isChord:
            total_notes += len(el.pitches)

    print(f"Total notes in score: {total_notes}")
    print(f"Total notes in hand.noteseq: {len(hand.noteseq)}")

    # Safety check
    if len(hand.noteseq) < total_notes:
        print(f"WARNING: Not enough notes in hand.noteseq ({len(hand.noteseq)}) to annotate all score notes ({total_notes})")
        print("Will only annotate available notes")

    # Now do the annotation, but check array bounds
    idx = 0
    for el in p0.flat.getElementsByClass("GeneralNote"):
        if el.isNote:
            if idx < len(hand.noteseq):
                n = hand.noteseq[idx]
                if hand.lyrics:
                    el.addLyric(n.fingering)
                else:
                    el.articulations.append(Fingering(n.fingering))
                idx += 1
            else:
                print(f"Skipping note at index {idx} - out of bounds")
                # Add a default fingering or skip
                if not hand.lyrics:
                    el.articulations.append(Fingering("?"))
        elif el.isChord:
            for j, cn in enumerate(el.pitches):
                if idx < len(hand.noteseq):
                    n = hand.noteseq[idx]
                    if hand.lyrics:
                        nl = len(el.pitches) - j - 1  # Reverse index for lyrics
                        el.addLyric(n.fingering, nl)
                    else:
                        el.articulations.append(Fingering(n.fingering))
                    idx += 1
                else:
                    print(f"Skipping chord note at index {idx} - out of bounds")
                    # Add a default fingering or skip
                    if not hand.lyrics:
                        el.articulations.append(Fingering("?"))

    return sf


def annotate_PIG(hand, is_right=True):
    ans = []
    for n in hand.noteseq:
        onset_time = "{:.4f}".format(n.time)
        offset_time = "{:.4f}".format(n.time + n.duration)
        spelled_pitch = n.pitch
        onset_velocity = str(None)
        offset_velocity = str(None)
        channel = '0' if is_right else '1'
        finger_number = n.fingering if is_right else -n.fingering
        cost = n.cost
        ans.append((onset_time, offset_time, spelled_pitch, onset_velocity, offset_velocity, channel,
                    finger_number, cost, n.noteID))
    return ans


def annotate(args):
    hand_size = 'M'  # default
    if args.hand_size_XXS: hand_size = 'XXS'
    if args.hand_size_XS: hand_size = 'XS'
    if args.hand_size_S: hand_size = 'S'
    if args.hand_size_M: hand_size = 'M'
    if args.hand_size_L: hand_size = 'L'
    if args.hand_size_XL: hand_size = 'XL'
    if args.hand_size_XXL: hand_size = 'XXL'

    # Initialize callback if provided
    callback = getattr(args, 'callback', None)
    if not callback:
        callback = lambda measure=0, total=0, status="": None

    # Call callback with starting status
    callback(measure=0, total=args.n_measures, status="Initializing processing")

    xmlfn = args.filename
    if '.msc' in args.filename:
        try:
            xmlfn = str(args.filename).replace('.mscz', '.xml').replace('.mscx', '.xml')
            callback(measure=0, total=args.n_measures, status="Converting MuseScore file")
            print('..trying to convert your musescore file to', xmlfn)
            os.system(
                'musescore -f "' + args.filename + '" -o "' + xmlfn + '"')  # quotes avoid problems w/ spaces in filename
            sf = converter.parse(xmlfn)
            if not args.left_only:
                rh_noteseq = reader(sf, beam=args.rbeam)
            if not args.right_only:
                lh_noteseq = reader(sf, beam=args.lbeam)
        except:
            callback(measure=0, total=args.n_measures, status="Error converting file")
            print('Unable to convert file, try to do it from musescore.')
            sys.exit()

    elif '.txt' in args.filename:
        callback(measure=0, total=args.n_measures, status="Reading PIG file")
        if not args.left_only:
            rh_noteseq = reader_PIG(args.filename, args.rbeam)
        if not args.right_only:
            lh_noteseq = reader_PIG(args.filename, args.lbeam)
    elif '.mxl' in args.filename:
        # MXL files are compressed MusicXML files
        callback(measure=0, total=args.n_measures, status="Reading compressed MusicXML file")
        sf = converter.parse(args.filename)
        # set the n_measures to the number of measures in the score
        args.n_measures = len(sf.parts[args.rbeam].getElementsByClass('Measure'))
    else:
        xmlfn = args.filename
        callback(measure=0, total=args.n_measures, status="Parsing MusicXML file")
        sf = converter.parse(xmlfn)
        # set the n_measures to the number of measures in the score
        args.n_measures = len(sf.parts[args.rbeam].getElementsByClass('Measure'))

    # Process right hand if needed
    if not args.left_only:
        callback(measure=0, total=args.n_measures, status="Preparing right hand fingering")
        rh = Hand("right", hand_size)
        rh.verbose = not(args.quiet)
        if args.depth == 0:
            rh.autodepth = True
        else:
            rh.autodepth = False
            rh.depth = args.depth
        rh.lyrics = args.below_beam

        # Set the progress callback
        rh.set_progress_callback(callback)

        rh.noteseq = reader(sf, beam=args.rbeam)
        rh.generate(args.start_measure, args.n_measures)

    # Process left hand if needed
    if not args.right_only:
        callback(measure=args.n_measures//2 if args.n_measures > 1 else 0,
                total=args.n_measures,
                status="Preparing left hand fingering")
        lh = Hand("left", hand_size)
        lh.verbose = not(args.quiet)
        if args.depth == 0:
            lh.autodepth = True
        else:
            lh.autodepth = False
            lh.depth = args.depth
        lh.lyrics = args.below_beam

        # Set the progress callback
        lh.set_progress_callback(callback)

        lh.noteseq = reader(sf, beam=args.lbeam)
        lh.generate(args.start_measure, args.n_measures)

    # Final processing
    callback(measure=args.n_measures, total=args.n_measures, status="Writing output file")
    sf.write('xml', fp=args.outputfile)

    # Call final callback
    callback(measure=args.n_measures, total=args.n_measures, status="Processing complete")

if __name__ == '__main__':
    run_annotate('../scores/test_chord.xml', outputfile="test_chord_annotate.xml", right_only=True, musescore=True, n_measures=800, depth=0)
