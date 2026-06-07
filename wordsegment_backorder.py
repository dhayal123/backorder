import csv
import re


class NormalizedDictReader(csv.DictReader):
    def __init__(self, f, *args, **kwargs):
        super().__init__(f, *args, **kwargs)
        if self.fieldnames:
            self.fieldnames = [h.strip().upper().lstrip('\ufeff') for h in self.fieldnames]

    def __next__(self):
        row = super().__next__()
        return {k.strip().upper().lstrip('\ufeff'): v for k, v in row.items()}


def load_unigrams(file_path):
    unigram = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if not parts or not parts[0]:
                continue
            word = parts[0].lower()
            freq = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
            unigram[word] = freq
    return unigram


def load_bigrams(file_path):
    bigram = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                w1 = parts[0].lower()
                w2 = parts[1].lower()
                freq = int(parts[2]) if parts[2].isdigit() else 1
                bigram[(w1, w2)] = freq
    return bigram


def is_repeated_chars(word):
    return bool(re.search(r'(.)\1{2,}', word))


def segment_domain(domain, unigram, bigram, special_nums):
    domain = domain.lower()

    if len(domain) < 5:
        return (f"{len(domain)}L", [domain])

    if domain.isdigit():
        if len(domain) < 7:
            return (1, [domain])
        else:
            return ("JUNK", [])

    if any(c.isdigit() for c in domain) and not domain.isdigit():
        return ("JUNK", [])

    if domain in special_nums:
        return (1, [domain])
    if domain in unigram:
        return (1, [domain])
    if is_repeated_chars(domain):
        return ("JUNK", [])

    n = len(domain)
    dp = [None] * (n + 1)
    dp[n] = (0, [], 0)

    for i in range(n - 1, -1, -1):
        candidates = []
        for j in range(i + 1, n + 1):
            word = domain[i:j]
            if word in unigram or word in special_nums:
                if dp[j] is not None:
                    cand_words = [word] + dp[j][1]
                    cand_count = 1 + dp[j][0]
                    if cand_count <= 4 and all(w in unigram or w in special_nums for w in cand_words):
                        unigram_score = sum(unigram.get(w, 1) for w in cand_words)
                        bigram_score = sum(
                            bigram.get((cand_words[k], cand_words[k + 1]), 0)
                            for k in range(len(cand_words) - 1)
                        )
                        total_score = unigram_score + bigram_score
                        candidates.append((cand_count, cand_words, total_score))

        if candidates:
            min_words = min(c[0] for c in candidates)
            best = max((c for c in candidates if c[0] == min_words), key=lambda x: x[2])
            dp[i] = best
        else:
            dp[i] = None

    if dp[0] and all(w in unigram or w in special_nums for w in dp[0][1]):
        return (dp[0][0], dp[0][1])

    return ("JUNK", [])


def process_csv():
    unigram_file = '/Users/dhayalmani/Downloads/Reference/wordsegment/en-unigrams.txt'
    bigram_file = '/Users/dhayalmani/Downloads/Reference/wordsegment/en-bigrams.txt'
    input_file = '/Users/dhayalmani/Downloads/Data/backorder/blueorgreenbackorder.csv'
    output_file = '/Users/dhayalmani/Downloads/Data/backorder/bluegreenbackorder-segmented.csv'
    SPECIAL_NUMS = {"123", "247", "365", "360"}

    unigram = load_unigrams(unigram_file)
    bigram = load_bigrams(bigram_file)

    with open(input_file, 'r', encoding='utf-8-sig', newline='') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = NormalizedDictReader(infile)
        fieldnames = reader.fieldnames + ['WORDS', 'WORDCOUNT']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        total_processed = 0

        for row in reader:
            domain = row['DOMAIN'].split('.')[0]

            if domain.count('-') > 1:
                row['WORDCOUNT'] = 'JUNK'
                row['WORDS'] = ''
            elif '-' in domain:
                parts = domain.split('-')
                if len(parts) == 2:
                    left, right = parts
                    left_wc, left_words = segment_domain(left, unigram, bigram, SPECIAL_NUMS)
                    right_wc, right_words = segment_domain(right, unigram, bigram, SPECIAL_NUMS)

                    if left_wc == "JUNK" or right_wc == "JUNK":
                        row['WORDCOUNT'] = 'JUNK'
                        row['WORDS'] = ''
                    else:
                        left_count = 1 if (isinstance(left_wc, str) and left_wc.endswith('L')) else left_wc
                        right_count = 1 if (isinstance(right_wc, str) and right_wc.endswith('L')) else right_wc
                        word_count = (
                            (left_count if isinstance(left_count, int) else 0) +
                            (right_count if isinstance(right_count, int) else 0)
                        )

                        if word_count > 4:
                            row['WORDCOUNT'] = 'JUNK'
                            row['WORDS'] = ''
                        else:
                            row['WORDCOUNT'] = word_count
                            row['WORDS'] = ','.join(left_words + right_words)
                else:
                    row['WORDCOUNT'] = 'JUNK'
                    row['WORDS'] = ''
            else:
                word_count, words = segment_domain(domain, unigram, bigram, SPECIAL_NUMS)
                row['WORDCOUNT'] = word_count
                if isinstance(word_count, str) and word_count.endswith('L'):
                    row['WORDS'] = ','.join(words)
                elif isinstance(word_count, int):
                    row['WORDS'] = ','.join(words)
                else:
                    row['WORDS'] = ''

            writer.writerow(row)
            total_processed += 1
            if total_processed % 1000 == 0:
                print(f"{total_processed}/processed")

    print(f"Processing complete. Output written to {output_file}")


if __name__ == "__main__":
    process_csv()