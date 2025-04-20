(use-modules ((guix licenses)
              #:prefix license:)
             (guix packages)
             (guix download)
             (guix build-system python)
             (guix build-system pyproject)
             (gnu packages time)
             (gnu packages python-xyz)
             (guix git-download)
             (gnu packages python-check)
             (gnu packages python-web)
             (gnu packages certs)
             (gnu packages databases)
             (gnu packages check)
             (gnu packages python-build))

(define-public python-tatsu
  (package
    (name "python-tatsu")
    (version "5.13.1")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "tatsu" version))
       (sha256
        (base32 "04n0dgmfi89iyg2bvw9x7npvbr51zldlyqh8nfszk6nhxip2336z"))))
    (build-system pyproject-build-system)
    (arguments
     (list
      #:tests? #f)) ;TODO: enable
    (native-inputs (list python-setuptools python-wheel))
    (home-page "https://tatsu.readthedocs.io/en/stable/")
    (synopsis "PEG/Packrat parser generator for Python")
    (description
     "@code{TatSu} takes a grammar in a variation of EBNF as input, and
outputs a memoizing PEG/Packrat parser in Python.")
    (license license:bsd-4)))

(define-public python-ics
  (package
    (name "python-ics")
    (version "0.7.2")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "ics" version))
       (sha256
        (base32 "01cz428xy8bmgjzvx610p0haz50hrm7xg1wv4hsicf8hradm6hv7"))))
    (build-system pyproject-build-system)
    (arguments
     (list
      #:tests? #f)) ;TODO: enable
    (propagated-inputs (list python-arrow python-attrs python-dateutil
                             python-six python-tatsu))
    (native-inputs (list python-setuptools
                         python-wheel
                         python-pip
                         nss-certs-for-test
                         python-mypy
                         python-pytest-sugar
                         python-freezegun))
    (home-page "http://github.com/C4ptainCrunch/ics.py")
    (synopsis "Python icalendar (rfc5545) parser")
    (description "Python icalendar (rfc5545) parser.")
    (license license:asl2.0)))

(define-public python-aiohttp-client-cache
  (package
    (name "python-aiohttp-client-cache")
    (version "0.12.4")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "aiohttp_client_cache" version))
       (sha256
        (base32 "0rfjcxll4q53hmqbbng4l578b5qxp0m2fsxvydk1snvb2cbfh3z6"))))
    (build-system pyproject-build-system)
    (arguments (list #:tests? #f)) ;TODO
    (propagated-inputs (list python-aiobotocore
                             python-aiofiles
                             python-aiohttp
                             python-aiosqlite
                             python-attrs
                             python-itsdangerous
                             python-redis
                             python-url-normalize))
    (native-inputs (list python-poetry-core))
    (home-page "https://github.com/requests-cache/aiohttp-client-cache")
    (synopsis "Persistent cache for aiohttp requests")
    (description "Persistent cache for aiohttp requests.")
    (license license:expat)))

(concatenate-manifests
 (list (specifications->manifest (list "python@3.10" ;https://docs.python.org/ja/3.10/
                                       "python-aiohttp"
                                       "python-dotenv"
                                       "poetry"
                                       "python-sphinx"
                                       "python-myst-parser"
                                       "python-sphinx-intl"
                                       "python-mypy"))
       (packages->manifest (list python-ics python-aiohttp-client-cache
                                 python-isodate))))
